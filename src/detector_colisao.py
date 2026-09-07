#!/usr/bin/env python3

import os
import sys
import hashlib
import argparse
import time


def gerar_amostra_aleatoria(tamanho_bytes=10):
    return os.urandom(tamanho_bytes)



def testar_colisoes_algoritmo(nome_algoritmo, total_amostras=1000000, tamanho_bytes=10):
    mapa_hashes = {}
    colisoes = []

    inicio = time.time()

    for _ in range(total_amostras):
        amostra = gerar_amostra_aleatoria(tamanho_bytes)

        if nome_algoritmo == "sha1":
            hash_digest = hashlib.sha1(amostra).digest()
        elif nome_algoritmo == "sha256":
            hash_digest = hashlib.sha256(amostra).digest()
        else:
            hash_digest = hashlib.new(nome_algoritmo, amostra).digest()
        
        if hash_digest in mapa_hashes:
            amostra_existente = mapa_hashes[hash_digest]
            if amostra_existente != amostra:
                colisoes.append((amostra_existente, amostra, hash_digest.hex()))
        else:
            mapa_hashes[hash_digest] = amostra
    
    tempo_decorrido = time.time() - inicio
    hashes_unicos = len(mapa_hashes)

    return {
        "algoritmo": nome_algoritmo.upper(),
        "total_amostras": total_amostras,
        "hashes_unicos": hashes_unicos,
        "total_colisoes": len(colisoes),
        "colisoes": colisoes,
        "tempo_segundos": tempo_decorrido,
    }



def exibir_relatorio_experimento(resultados, tamanho_bytes=10):
    print("="*65)
    print("           EXPERIMENTO DE DETECÇÃO DE COLISÕES DE HASH")
    print("="*65)

    total_amostras = resultados[0]["total_amostras"]
    print(f"[*] Parâmetros: {total_amostras:,} amostras | {tamanho_bytes} bytes aleatórios por amostra\n")

    for i, res in enumerate(resultados, start=1):
        alg = res["algoritmo"]
        status = "(Obsoleto)" if alg == "SHA1" else "(Seguro)"
        print(f"[{i}] Execução: {alg} {status}")
        print(f"    - Tempo de execução:       {res['tempo_segundos']:.4f} s")
        print(f"    - Hashes processados:      {res['total_amostras']:,}")
        print(f"    - Hashes únicos:           {res['hashes_unicos']:,}")
        print(f"    - Colisões detectadas:     {res['total_colisoes']}")

        if res["total_colisoes"] > 0:
            print("    [!] Detalhes das colisões:")
            for c in res["colisoes"][:5]:
                print(f"        - Entrada 1: {c[0].hex()} | Entrada 2: {c[1].hex()} -> Hash: {c[2]}")
        print()


    print("="*65)
    print("RESUMO COMPARATIVO:")
    for res in resultados:
        print(f"  - {res['algoritmo']:<7}: {res['total_amostras']:,} hashes em {res['tempo_segundos']:.4f}s | {res['total_colisoes']} colisões")
    print("="*65)



def main():
    parser = argparse.ArgumentParser(
        description="Detector de Colisões de Hash SHA-1 vs SHA-256 em Grande Escala."
    )
    parser.add_argument(
        "--amostras", "-n",
        type=int,
        default=1000000,
        help="Quantidade de amostras aleatórias a serem testadas (padrão: 1.000.000)"
    )
    parser.add_argument(
        "--tamanho-bytes", "-b",
        type=int,
        default=10,
        help="Tamanho em bytes de cada amostra aleatória gerada via os.urandom (padrão: 10 bytes)"
    )
    parser.add_argument(
        "--algoritmo", "-a",
        type=str,
        choices=["sha1", "sha256", "ambos"],
        default="ambos",
        help="Algoritmo a ser testado: sha1, sha256 ou ambos (padrão: ambos)"
    )

    args = parser.parse_args()
    resultados = []
    
    if args.algoritmo in ["sha1", "ambos"]:
        res_sha1 = testar_colisoes_algoritmo("sha1", total_amostras=args.amostras, tamanho_bytes=args.tamanho_bytes)
        resultados.append(res_sha1)
    
    if args.algoritmo in ["sha256", "ambos"]:
        res_sha256 = testar_colisoes_algoritmo("sha256", total_amostras=args.amostras, tamanho_bytes=args.tamanho_bytes)
        resultados.append(res_sha256)
    
    exibir_relatorio_experimento(resultados, tamanho_bytes=args.tamanho_bytes)



if __name__ == "__main__":
    main()