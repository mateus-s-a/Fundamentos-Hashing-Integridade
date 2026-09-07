#!/usr/bin/env python3

import hashlib
import sys
import os
import hashlib
import argparse
import time


def carregar_dicionario_senhas(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Erro: Dicionário '{caminho_arquivo}' não encontrado", file=sys.stderr)
        sys.exit(1)
    
    senhas = []
    with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            senha = linha.rstrip("\r\n")
            if senha:
                senhas.append(senha)
    return senhas



def carregar_hashes_com_salt(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Erro: Arquivo de hashes '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    registros = []
    with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
        for num_linha, linha in enumerate(f, start=1):
            linha_limpa = linha.strip()
            
            if not linha_limpa or linha_limpa.startswith("#"):
                continue
            
            partes = linha_limpa.split(":")
            if len(partes) == 2:
                salt_hex, hash_hex = partes[0].strip().lower(), partes[1].strip().lower()
                registros.append((salt_hex, hash_hex))
            else:
                print(f"[!] Aviso: Linha {num_linha} ignorada por formato inválido", file=sys.stderr)
    return registros



def quebrar_hashes_com_salt(caminho_hashes, caminho_dicionario):
    registros_alvo = carregar_hashes_com_salt(caminho_hashes)
    senhas_dicionario = carregar_dicionario_senhas(caminho_dicionario)

    # cache de pré-computação por salt: {salt_hex: {hash_gerado: senha}}
    cache_salts = {}
    salts_reutilizados = 0
    quebradas = 0
    nao_encontradas = 0

    for salt_hex, hash_alvo in registros_alvo:
        
        # Se o salt já foi pré-computado anteriormente no lote, reaproveita o dicionário
        if salt_hex in cache_salts:
            mapa_hash_senha = cache_salts[salt_hex]
            salts_reutilizados += 1
        else:
            # Pré-computação para o novo salt
            mapa_hash_senha = {}
            try:
                salt_bytes = bytes.fromhex(salt_hex)
            except ValueError:
                print(f"[!] Erro: Salt '{salt_hex}' inválido", file=sys.stderr)
                print(f"{salt_hex}:{hash_alvo} -> NAO_ENCONTRADA")
                nao_encontradas += 1
                continue

            for senha in senhas_dicionario:
                dados = salt_bytes + senha.encode("utf-8")
                hash_calc = hashlib.sha256(dados).hexdigest()
                mapa_hash_senha[hash_calc] = senha
            
            cache_salts[salt_hex] = mapa_hash_senha
        
        # Verificação do hash alvo
        if hash_alvo in mapa_hash_senha:
            senha_encontrada = mapa_hash_senha[hash_alvo]
            print(f"{salt_hex}:{hash_alvo} -> {senha_encontrada}")
            quebradas += 1
        else:
            print(f"{salt_hex}:{hash_alvo} -> NAO_ENCONTRADA")
            nao_encontradas += 1
    
    return quebradas, nao_encontradas, len(registros_alvo), len(cache_salts), salts_reutilizados



def main():
    parser = argparse.ArgumentParser(
        description="Quebra de Hashes SHA-256 com Salt via Ataque de Dicionário Inteligente"
    )
    parser.add_argument(
        "hashes",
        type=str,
        help="Caminho do arquivo de hashes com salt (ex: hashes_com_salt.txt)"
    )
    parser.add_argument(
        "dicionario",
        type=str,
        help="Caminho do dicionário de senhas (ex: senhas_comuns.txt)"
    )

    args = parser.parse_args()

    inicio = time.time()
    quebradas, nao_encontradas, total, salts_unicos, reuso = quebrar_hashes_com_salt(args.hashes, args.dicionario)
    duracao = time.time() - inicio

    print(
        f"\n[+] Concluído em {duracao:.4f}s | Total: {total} | Quebradas: {quebradas} | Não encontradas: {nao_encontradas} | Salts Únicos: {salts_unicos} | Otimizações de Cache: {reuso}",
        file=sys.stderr
    )


if __name__ == "__main__":
    main()