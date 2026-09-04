import sys
import os
import hashlib
import argparse
import time


def carregar_linhas(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Erro: Arquivo '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    linhas = []
    with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            item = linha.strip()
            if item and not item.startswith("#"):
                linhas.append(item)
    return linhas



def carregar_dicionario_senhas(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Erro: Dicionário '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    senhas = []
    with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            senha = linha.rstrip("\r\n")
            if senha:
                senha.append(senha)
    return senhas



def quebrar_hashes_sem_salt(caminho_hashes, caminho_dicionario):
    hashes_alvo = carregar_linhas(caminho_hashes)
    senhas_dicionario = carregar_dicionario_senhas(caminho_dicionario)

    # Pré-computação do dicionário em memória para otimização de bsuca O(1) manual
    # usando apenas hashlib unitário conforme permitido
    tabela_dicionario = {}
    for senha in senhas_dicionario:
        hash_calc = hashlib.sha256(senha.encode("utf-8")).hexdigest()
        if hash_calc not in tabela_dicionario:
            tabela_dicionario[hash_calc] = senha
    
    quebradas = 0
    nao_encontradas = 0


    # iteração sobre os hashes alvo e exibição no formato padrão
    for hash_alvo in hashes_alvo:
        hash_normalizado = hash_alvo.lower()
        if hash_normalizado in tabela_dicionario:
            senha_encontrada = tabela_dicionario[hash_normalizado]
            print(f"{hash_alvo}:{senha_encontrada}")
            quebradas += 1
        else:
            print(f"{hash_alvo}:NAO_ENCONTRADA")
            nao_encontradas += 1
    
    return quebradas, nao_encontradas, len(hashes_alvo)



def main():
    parser = argparse.ArgumentParser(
        description="Quebra de Hashes SHA-256 sem Salt via Ataque de Dicionário"
    )
    parser.add_argument(
        "hashes",
        type=str,
        help="Caminho do arquivo de hashes alvo (ex: hashes_sem_salt.txt)"
    )
    parser.add_argument(
        "dicionario",
        type=str,
        help="Caminho do arquivo de dicionário de senhas (ex: senhas_comuns.txt)"
    )

    args = parser.parse_args()

    inicio = time.time()
    quebradas, nao_encontradas, total = quebrar_hashes_sem_salt(args.hashes, args.dicionario)
    duracao = time.time() - inicio

    # saída informativa opcional em 'stderr' para não poluir o 'stdout' que pode ser redirecionado
    print(
        f"\n[+] Concluído em {duracao:.4f}s | Total: {total} | Quebradas: {quebradas} | Não encontradas: {nao_encontradas}",
        file=sys.stderr
    )



if __name__ == "__main__":
    main()