#!/usr/bin/env python3

import os
import sys
import hashlib
import argparse

# tamanho padrão do bloco para leitura em chunks (4 KB)
TAMANHO_BLOCO = 4096


def calcular_hash_arquivo(caminho_arquivo, tamanho_bloco=TAMANHO_BLOCO):
    sha256 = hashlib.sha256()

    try:
        with open(caminho_arquivo, "rb") as arq:
            while bloco := arq.read(tamanho_bloco):
                sha256.update(bloco)
        return sha256.hexdigest()
    
    except (PermissionError, FileNotFoundError, OSError) as erro:
        print(f"[!] Erro ao ler arquivo '{caminho_arquivo}': {erro}", file=sys.stderr)
        return None



def mapear_diretorio(diretorio_alvo, arquivo_hashes_ignorar=None):
    hashes_atuais = {}
    caminho_ignorar_abs = os.path.abspath(arquivo_hashes_ignorar) if arquivo_hashes_ignorar else None

    if not os.path.exists(diretorio_alvo):
        print(f"[!] Diretório '{diretorio_alvo}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    for raiz, _, arquivos in os.walk(diretorio_alvo):
        for nome_arquivo in sorted(arquivos):
            caminho_completo = os.path.join(raiz, nome_arquivo)

            # evita incluir o próprio arquivo hashes.txt se ele estiver dentro da pasta analisada
            if caminho_ignorar_abs and os.path.abspath(caminho_completo) == caminho_ignorar_abs:
                continue

            caminho_relativo = os.path.relpath(caminho_completo, start=diretorio_alvo)
            caminho_padronizado = os.path.normpath(caminho_relativo).replace("\\", "/")

            hash_calculado = calcular_hash_arquivo(caminho_completo)
            if hash_calculado is not None:
                hashes_atuais[caminho_padronizado] = hash_calculado

        return hashes_atuais



def salvar_hashes(hashes_dict, caminho_saida="hashes.txt"):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for caminho, hash_val in sorted(hashes_dict.items()):
            f.write(f"{caminho}:{hash_val}\n")
    print(f"[*] Base de hashes salva com sucesso em '{caminho_saida}' ({len(hashes_dict)} arquivos registrados).")



def carregar_hashes_salvos(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Arquivo de registro de hashes '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    
    hashes_salvos = {}
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("#"):
                continue
            partes = linha_limpa.rsplit(":", 1)
            if len(partes) == 2:
                caminho, hash_val = partes[0].strip(), partes[1].strip()
                hashes_salvos[caminho] = hash_val
    
    return hashes_salvos


def verificar_integridade(diretorio_alvo, caminho_hashes_base="hashes.txt"):
    print(f"[*] Verificando integridade do diretório '{diretorio_alvo}' contra base '{caminho_hashes_base}'...\n")

    hashes_salvos = carregar_hashes_salvos(caminho_hashes_base)
    hashes_atuais = mapear_diretorio(diretorio_alvo, arquivo_hashes_ignorar=caminho_hashes_base)

    arquivos_salvos_set = set(hashes_salvos.keys())
    arquivos_atuais_set = set(hashes_atuais.keys())

    novos = sorted(list(arquivos_atuais_set - arquivos_salvos_set))
    removidos = sorted(list(arquivos_salvos_set - arquivos_atuais_set))

    comuns = arquivos_salvos_set.intersection(arquivos_atuais_set)
    modificados = []
    inalterados = []

    for arq in sorted(comuns):
        if hashes_atuais[arq] == hashes_salvos[arq]:
            inalterados.append(arq)
        else:
            modificados.append(arq)
    
    # *** exibição do relatório de status formatado ***
    print("=" * 60)
    print("           RELATÓRIO DE INTEGRIDADE DE ARQUIVOS")
    print("=" * 60)

    print(f"\n[+] Arquivos Novos ({len(novos)}):")
    if novos:
        for item in novos:
            print(f"    + {item} (Hash: {hashes_atuais[item]})")
    else:
        print("    (nenhum)")
    
    print(f"\n[-] Arquivos Removidos ({len(removidos)}):")
    if removidos:
        for item in removidos:
            print(f"    + {item} (Hash anterior: {hashes_salvos[item]})")
    else:
        print("    (nenhum)")
    
    print(f"\n[!] Arquivos Modificados ({len(modificados)}):")
    if modificados:
        for item in modificados:
            print(f"    ! {item}")
            print(f"      Hash anterior: {hashes_salvos[item]})")
            print(f"      Hash atual: {hashes_atuais[item]})")
    else:
        print("    (nenhum)")
    
    print(f"\n[=] Arquivos Inalterados ({len(inalterados)}):")
    if inalterados:
        for item in inalterados:
            print(f"    = {item}")
    else:
        print("    (nenhum)")
    
    print("\n" + "="*60)
    print(f"RESUMO: Total={len(arquivos_atuais_set)} | Inalterados={len(inalterados)} | Modificados={len(modificados)} | Novos={len(novos)} | Removidos={len(removidos)}")
    print("="*60)



def main():
    parser = argparse.ArgumentParser(
        description="Verificador de Integridade de Arquivos via SHA-256 (Leitura em Chunks)"
    )
    parser.add_argument(
        "diretório",
        type=str,
        help="Caminho do diretório a ser mapeado ou verificado"
    )
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="Executa a verificação de integridade comparando com o arquivo de hashes existente"
    )
    parser.add_argument(
        "--base",
        type=str,
        default="hashes.txt",
        help="Caminho do arquivo hashes.txt para leitura ou gravação"
    )

    args = parser.parse_args()

    if args.verificar:
        verificar_integridade(args.diretorio, caminho_hashes_base=args.base)
    else:
        hashes = mapear_diretorio(args.diretorio, arquivo_hashes_ignorar=args.base)
        salvar_hashes(hashes, caminho_saida=args.base)



if __name__ == "__main__":
    main()