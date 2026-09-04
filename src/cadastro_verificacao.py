#!/usr/bin/env python3

import os
import sys
import hashlib
import argparse


def carregar_base_usuarios(caminho_arquivo):
    usuarios = {}
    if not os.path.exists(caminho_arquivo):
        return usuarios
    
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for num_linha, linha in enumerate(f, start=1):
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("#"):
                continue
            
            partes = linha_limpa.split(":")
            if len(partes) == 3:
                user, salt_h, hash_h = partes[0].strip(), partes[1].strip(), partes[2].strip()
                usuarios[user] = (salt_h, hash_h)
            
            else:
                print(f"[!] Aviso: Linha {num_linha} em formato inválido no arquivo '{caminho_arquivo}'.", file=sys.stderr)
    return usuarios



def salvar_base_usuarios(usuarios_dict, caminho_arquivo):
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        for user in sorted(usuarios_dict.keys()):
            salt_h, hash_h = usuarios_dict[user]
            f.write(f"{user}:{salt_h}:{hash_h}\n")



def cadastrar_usuario(usuario, senha, caminho_arquivo="usuarios.txt"):
    usuarios = carregar_base_usuarios(caminho_arquivo)

    # 1. Gerar salt aleatório criptograficamente seguro de 16 bytes
    salt_bytes = os.urandom(16)
    salt_hex = salt_bytes.hex()

    # 2. Concatenar salt + senha (em bytes)
    senha_bytes = senha.encode("utf-8")
    dados_concatenados = salt_bytes + senha_bytes

    # 3. Calcular o hash SHA-256
    hash_calculado = hashlib.sha256(dados_concatenados).hexdigest()

    # 4. Salvar no dicionário e persistir em arquivo
    ja_existia = usuario in usuarios
    usuarios[usuario] = (salt_hex, hash_calculado)
    salvar_base_usuarios(usuarios, caminho_arquivo)

    if ja_existia:
        print(f"[*] Senha do usuário '{usuario}' atualiza com sucesso em '{caminho_arquivo}'.")
    else:
        print(f"[+] Usuário '{usuario}' cadastrado com sucesso em '{caminho_arquivo}'.")
    print(f"    Salt (Hex): {salt_hex}")
    print(f"    Hash SHA-256: {hash_calculado}")



def verificar_autenticacao(usuario, senha, caminho_arquivo="usuarios.txt"):
    usuarios = carregar_base_usuarios(caminho_arquivo)

    if usuario not in usuarios:
        print("Acesso negado")
        return False
    
    salt_hex, hash_salvo = usuarios[usuario]

    try:
        salt_bytes = bytes.fromhex(salt_hex)
    except ValueError:
        print(f"[!] Erro de decodificação do salt para o usuário '{usuario}'.", file=sys.stderr)
        print("Acesso negado")
        return False
    
    senha_bytes = senha.encode("utf-8")
    dados_concatenados = salt_bytes + senha_bytes
    hash_tentativa = hashlib.sha256(dados_concatenados).hexdigest()

    if hash_tentativa.lower() == hash_salvo.lower():
        print("Acesso permitido")
        return True
    else:
        print("Acesso negado")
        return False



def main():
    parser = argparse.ArgumentParser(
        description="Módulo de Cadastro e Autenticação de Usuários com Salt SHA-256"
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument(
        "--cadastrar",
        nargs=2,
        metavar=("USUARIO", "SENHA"),
        help="Cadastra um novo usuário gerando salt criptográfico seguro"
    )
    grupo.add_argument(
        "--verificar",
        nargs=2,
        metavar=("USUARIO", "SENHA"),
        help="Verifica as credenciais de um usuário cadastrado"
    )
    parser.add_argument(
        "--arquivo",
        type=str,
        default="usuarios.txt",
        help="Caminho do arquivo de base de usuários (padrão: usuarios.txt)"
    )

    args = parser.parse_args()

    if args.cadastrar:
        user, pwd = args.cadastrar
        cadastrar_usuario(user, pwd, caminho_arquivo=args.arquivo)
    elif args.verificar:
        user, pwd = args.verificar
        verificar_autenticacao(user, pwd, caminho_arquivo=args.arquivo)


if __name__ == "__main__":
    main()