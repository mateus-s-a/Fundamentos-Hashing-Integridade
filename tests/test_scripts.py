#!/usr/bin/env python3

import unittest
import os
import shutil
import tempfile
import subprocess
import hashlib
import sys


class TestFase2Scripts(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_fase2_")
        self.src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    

    # Testa o script 'verificador_integridade.py' em todas as 4 classificações de status
    def test_verificador_integridade(self):
        pasta_alvo = os.path.join(self.temp_dir, "alvo")
        os.makedirs(os.path.join(pasta_alvo, "sub"), exist_ok=True)

        arq1 = os.path.join(pasta_alvo, "arq1.txt")
        arq2 = os.path.join(pasta_alvo, "sub", "arq2.txt")
        arq3 = os.path.join(pasta_alvo, "arq3.txt")

        with open(arq2, "w") as f: f.write("Conteudo 2")
        with open(arq1, "w") as f: f.write("Conteudo 1")
        with open(arq3, "w") as f: f.write("Conteudo 3")

        hashes_base = os.path.join(self.temp_dir, "hashes.txt")
        script = os.path.join(self.src_dir, "verificador_integridade.py")

        # 1. Gerar base
        res_gerar = subprocess.run([sys.executable, script, pasta_alvo, "--base", hashes_base], capture_output=True, text=True)
        self.assertEqual(res_gerar.returncode, 0)
        self.assertTrue(os.path.exists(hashes_base))

        # 2. Verificar inalterado
        res_verif1 = subprocess.run([sys.executable, script, pasta_alvo, "--verificar", "--base", hashes_base], capture_output=True, text=True)
        self.assertEqual(res_verif1.returncode, 0)
        self.assertIn("Arquivos Inalterados (3)", res_verif1.stdout)

        # 3. Alterar arquivos (1 modificado, 1 removido, 1 novo, 1 inalterado)
        with open(arq1, "w") as f: f.write("Conteudo 1 MODIFICADO")
        os.remove(arq2)
        arq4 = os.path.join(pasta_alvo, "arq4.txt")
        with open(arq4, "w") as f: f.write("Conteudo 4 NOVO")

        res_verif2 = subprocess.run([sys.executable, script, pasta_alvo, "--verificar", "--base", hashes_base], capture_output=True, text=True)
        self.assertIn("Arquivos Novos (1)", res_verif2.stdout)
        self.assertIn("Arquivos Removidos (1)", res_verif2.stdout)
        self.assertIn("Arquivos Modificados (1)", res_verif2.stdout)
        self.assertIn("Arquivos Inalterados (1)", res_verif2.stdout)


    # Testa o script 'quebra_sem_salt.py' com dicionário e hashes alvo
    def test_quebra_sem_salt(self):
        dict_path = os.path.join(self.temp_dir, "dict.txt")
        hashes_path = os.path.join(self.temp_dir, "hashes.txt")

        with open(dict_path, "w") as f:
            f.write("admin\n123456\nsenha123\n")

        h_admin = hashlib.sha256(b"admin").hexdigest()
        h_desconhecido = hashlib.sha256(b"desconhecida_xyz").hexdigest()

        with open(hashes_path, "w") as f:
            f.write(f"{h_admin}\n{h_desconhecido}\n")
        
        script = os.path.join(self.src_dir, "quebra_sem_salt.py")
        res = subprocess.run([sys.executable, script, hashes_path, dict_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn(f"{h_admin}:admin", res.stdout)
        self.assertIn(f"{h_desconhecido}:NAO_ENCONTRADA", res.stdout)
    

    # Testa cadastro e autenticação de usuários com salt de 16 bytes
    def test_cadastro_verificacao(self):
        db_path = os.path.join(self.temp_dir, "usuarios.txt")
        script = os.path.join(self.src_dir, "cadastro_verificacao.py")

        # 1. Cadastrar
        res_cad1 = subprocess.run([sys.executable, script, "--cadastrar", "user1", "SenhaSegura1", "--arquivo", db_path], capture_output=True, text=True)
        self.assertEqual(res_cad1.returncode, 0)
        self.assertTrue(os.path.exists(db_path))

        # Cadastrar segundo usuário com mesma senha para conferir 'salt' distinto
        res_cad2 = subprocess.run([sys.executable, script, "--cadastrar", "user2", "SenhaSegura1", "--arquivo", db_path], capture_output=True, text=True)
        self.assertEqual(res_cad2.returncode, 0)

        with open(db_path) as f:
            linhas = [l.strip() for l in f if l.strip()]
        self.assertEqual(len(linhas), 2)
        u1, s1, h1 = linhas[0].split(":")
        u2, s2, h2 = linhas[1].split(":")
        self.assertEqual(len(bytes.fromhex(s1)), 16)
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(h1, h2)

        # 2. Verificar sucesso
        res_login_ok = subprocess.run([sys.executable, script, "--verificar", "user1", "SenhaSegura1", "--arquivo", db_path], capture_output=True, text=True)
        self.assertIn("Acesso permitido", res_login_ok.stdout)

        # 3. Verificar senha errada
        res_login_fail = subprocess.run([sys.executable, script, "--verificar", "user1", "SenhaErrada", "--arquivo", db_path], capture_output=True, text=True)
        self.assertIn("Acesso negado", res_login_fail.stdout)
    

    # Testa quebra com 'quebra_com_salt.py' com pré-computação para 'salts' repetidos
    def test_quebra_com_salt(self):
        dict_path = os.path.join(self.temp_dir, "dict.txt")
        hashes_path = os.path.join(self.temp_dir, "hashes.txt")

        with open(dict_path, "w") as f:
            f.write("admin\n123456\n")
        
        salt1 = os.urandom(16)
        h1 = hashlib.sha256(salt1 + b"admin").hexdigest()
        h2 = hashlib.sha256(salt1 + b"123456").hexdigest()

        with open(hashes_path, "w") as f:
            f.write(f"{salt1.hex()}:{h1}\n")
            f.write(f"{salt1.hex()}:{h2}\n")
        
        script = os.path.join(self.src_dir, "quebra_com_salt.py")
        res = subprocess.run([sys.executable, script, hashes_path, dict_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn(f"{salt1.hex()}:{h1} -> admin", res.stdout)
        self.assertIn(f"{salt1.hex()}:{h2} -> 123456", res.stdout)


    # Testa o script 'detector_colisao.py' (Fase 4 - Extra com Bônus)
    def test_detector_colisao(self):
        script = os.path.join(self.src_dir, "detector_colisao.py")
        res = subprocess.run([sys.executable, script, "--amostras", "5000", "--tamanho-bytes", "10", "--algoritmo", "ambos"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("EXPERIMENTO DE DETECÇÃO DE COLISÕES DE HASH", res.stdout)
        self.assertIn("SHA1 (Obsoleto)", res.stdout)
        self.assertIn("SHA256 (Seguro)", res.stdout)
        self.assertIn("RESUMO COMPARATIVO", res.stdout)




if __name__ == "__main__":
    unittest.main()