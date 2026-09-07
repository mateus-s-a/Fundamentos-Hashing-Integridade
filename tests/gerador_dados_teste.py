#!/usr/bin/env python3
import hashlib
import os
import random

# Dicionario com senhas comuns + 10.000 senhas numéricas
senhas_comuns = [
    "admin", "123456", "senha123", "password", "letmein", "welcome",
    "12345678", "root", "master", "qwerty", "iloveyou", "princess",
    "123456789", "football", "monkey", "dragon", "shadow", "secret",
    "amor", "102030", "matrix", "gabriel", "lucas", "beatriz", "sucesso"
]
dicionario_completo = senhas_comuns + [str(i).zfill(4) for i in range(10000)]

os.makedirs("dados", exist_ok=True)

# Salvar dicionário
with open("dados/senhas_comuns.txt", "w", encoding="utf-8") as f:
    for s in dicionario_completo:
        f.write(s + "\n")

# hashes SEM salt (válidas do dicionário e inválidas)
senhas_alvo_sem_salt = [
    "admin", "123456", "dragon", "senha123", "root", "football", 
    "12345678", "iloveyou", "master", "amor", "matrix", "102030",
    "senha_falsa_abc", "inexistente999", "9999", "0000", "5555"
]
with open("dados/hashes_sem_salt.txt", "w", encoding="utf-8") as f:
    for s in senhas_alvo_sem_salt:
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        f.write(h + "\n")

# hashes COM salt misturando salts reutilizados e salts únicos
salts_reutilizaveis = [os.urandom(16) for _ in range(3)]

# Lista de senhas de teste
senhas_para_salt = [
    "admin", "senha123", "monkey", "football", "123456", 
    "root", "master", "shadow", "amor", "matrix", "senha_falsa",
    "usuario1", "usuario2", "usuario3", "usuario4", "usuario5"
]

alvos_com_salt = []
for i, pwd in enumerate(senhas_para_salt):
    # A cada 3 itens, é reutilizado um salt
    if i % 3 == 0:
        salt_escolhido = salts_reutilizaveis[i % len(salts_reutilizaveis)]
    else:
        # Geração de um salt novo
        salt_escolhido = os.urandom(16)
        
    alvos_com_salt.append((salt_escolhido, pwd))
    
    if i % 4 == 0:
        alvos_com_salt.append((salts_reutilizaveis[0], pwd + "extra"))

with open("dados/hashes_com_salt.txt", "w", encoding="utf-8") as f:
    for salt_bytes, pwd in alvos_com_salt:
        hash_calc = hashlib.sha256(salt_bytes + pwd.encode('utf-8')).hexdigest()
        f.write(f"{salt_bytes.hex()}:{hash_calc}\n")

print("[+] Arquivos gerados com sucesso na pasta 'dados/'!")
print(f"- senhas_comuns.txt: {len(dicionario_completo)} senhas.")
print(f"- hashes_sem_salt.txt: {len(senhas_alvo_sem_salt)} hashes.")
print(f"- hashes_com_salt.txt: {len(alvos_com_salt)} hashes (mistura de salts exclusivos e reutilizados).")