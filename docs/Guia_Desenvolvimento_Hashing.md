# Guia de Desenvolvimento e Implementação: Atividade Prática de Hashing

## 1. Resumo Operacional

Este documento serve como roteiro técnico e planejamento estruturado para a execução da atividade prática da disciplina de **Segurança de Sistemas Computacionais**.

| Requisito Operacional | Especificação |
| :--- | :--- |
| **Dupla de Desenvolvimento** | **Mateus & Lorena** |
| **Data de Início** | 02/09/2026 |
| **Data Limite de Entrega** | **07/09/2026 até às 23h59** |
| **Formato de Submissão** | Arquivo único `.zip` contendo os scripts em Python (`.py`) e o Relatório Técnico em PDF (máx. 5 páginas). |
| **Controle de Versão** | Repositório no GitHub (link obrigatoriamente citado no relatório PDF e no `README.md`). |

---

## 2. Cronograma Sugerido de Execução (02/09 a 07/09)

* **02/09 (Quarta-feira):** Alinhamento inicial da dupla, criação do repositório no GitHub e **Fase 1 / Parte 1 Teórica (Lorena)**.
* **03/09 e 04/09 (Quinta e Sexta-feira):** **Fase 2 / Parte 2 Desenvolvimento dos 4 Scripts em Python (Mateus)**. `[CONCLUÍDO]`
* **05/09 e 06/09 (Sábado e Domingo):** **Fase 4 / Parte 4 Extra Bônus `detector_colisao.py` (Mateus)**. `[CONCLUÍDO]`
* **06/09 (Domingo):** **Fase 3 / Parte 3 Análise Comparativa, Métricas, KDF e Capturas de Tela (Lorena)**.
* **07/09 (Segunda-feira):** **Fase 5 / Revisão Conjunta (Mateus & Lorena)** — Testes de fumaça, conferência do PDF (máx 5 páginas), empacotamento `.zip` e submissão final até às 23h59.

---

## 3. Restrições Técnicas Rigorosas

* **Bibliotecas Externas de Alto Nível:** É estritamente proibido o uso de módulos prontos como `passlib`, `bcrypt` ou ferramentas de cracking externas como `hashcat` e `john` para resolver a tarefa de forma automatizada.
* **Uso da biblioteca hashlib:** A biblioteca nativa `hashlib` só é permitida de forma unitária (exclusivamente para o cálculo matemático do hash individual). Toda a lógica de comparação, busca, geração de salts e navegação em arquivos deve ser desenvolvida de forma autoral.
* **IA e Integridade:** O código deve ser autoral. Não será aceito material gerado integralmente por Inteligência Artificial ou trechos copiados.

---

## 4. Divisão de Tarefas por Fase e Responsável DEDICADO

### Fase 1: Conceitos Teóricos — Parte 1 do Enunciado (**Responsável: LORENA**)
* **1.1 Função Hash Criptográfica:** Conceituação e detalhamento das 3 propriedades essenciais (resistência à pré-imagem, segunda pré-imagem e colisão).
* **1.2 Hash vs. Cifragem:** Explicar a diferença arquitetônica fundamental entre hash (unidirecional) e criptografia/cifragem (bidirecional).
* **1.3 Colisões e SHA-1:** O que é uma colisão e justificativa técnica da obsolescência do SHA-1 na segurança moderna.
* **1.4 Mecanismo de Salt:** Finalidade do salt e por que é indispensável no armazenamento seguro de senhas.
* **1.5 Tipos de Ataques a Hashes:** Diferenciação detalhada entre força bruta, dicionário e rainbow tables.
* **Estruturação Inicial do PDF:** Configuração da estrutura base do Relatório Técnico para receber as análises.

---

### Fase 2: Implementações em Python — Parte 2 do Enunciado (**Responsável: MATEUS**) — `[CONCLUÍDO]`
* **Item 2.1 — `verificador_integridade.py`:**
  * Varredura e mapeamento recursivo de diretórios.
  * Leitura eficiente em blocos (*chunks* de 4096 bytes) para suportar arquivos > 1 GB sem esgotar RAM.
  * Cálculo de SHA-256 e salvamento no padrão `caminho:hash` em `hashes.txt`.
  * Modo `--verificar` com geração de relatório de status (novos, removidos, modificados e inalterados).
* **Item 2.2 — `quebra_sem_salt.py`:**
  * Carregamento de `hashes_sem_salt.txt` e `senhas_comuns.txt`.
  * Lógica de busca e comparação manual hash-a-hash.
  * Exibição formatada: `hash:senha_encontrada` ou `hash:NAO_ENCONTRADA`.
* **Item 2.3 — `cadastro_verificacao.py`:**
  * Modo `--cadastrar usuario senha`: geração de salt aleatório de 16 bytes via `os.urandom`, concatenação em bytes, cálculo de SHA-256 e gravação no padrão `usuario:salt_hex:hash_hex` em `usuarios.txt`.
  * Modo `--verificar usuario senha`: busca do registro, extração do salt, validação e exibição de `"Acesso permitido"` / `"Acesso negado"`.
* **Item 2.4 — `quebra_com_salt.py`:**
  * Extração de salt e hash por linha de `hashes_com_salt.txt`.
  * Teste contra `senhas_comuns.txt` calculando `SHA-256(salt + senha)`.
  * Exibição formatada: `salt:hash -> senha` ou `salt:hash -> NAO_ENCONTRADA`.
  * **Desafio Bônus:** Otimização com pré-computação em caso de salts reutilizados no lote.

---

### Fase 4: Desafio Extra Opcional (Com Bônus) — Parte 4 do Enunciado (**Responsável: MATEUS**) — `[CONCLUÍDO]`
* **Script `detector_colisao.py`:**
  * Gerar 1.000.000 de strings aleatórias via `os.urandom(10)`.
  * Calcular hashes no algoritmo SHA-1 (obsoleto) e reportar o total de colisões.
  * Repetir o mesmo experimento substituindo o algoritmo por SHA-256 e comparar os resultados.
* **Pergunta de Reflexão:** Redação da resposta técnica explicando a preferência pelo SHA-256 mesmo com colisões raras nessa escala documentada no `README.md`.

---

### Fase 3: Análise Comparativa & Documentação — Parte 3 do Enunciado (**Responsável: LORENA**)
* **Coleta e Formatação de Métricas:** Medição dos tempos de execução e contabilização das senhas quebradas nos cenários 2.2 e 2.4.
* **Justificativa Analítica de Desempenho:** Redação sobre o motivo e impacto do salt na desaceleração dos ataques.
* **Análise de Casos de Segurança:** Estudo detalhado dos cenários (mesmo salt vs salts diferentes para a mesma senha).
* **Proposta de Evolução Conceitual:** Apresentação teórica de KDFs (PBKDF2/Argon2/bcrypt) para proteção de senhas.
* **Evidências de Execução:** Organização e captura de telas (*prints*) de todas as execuções bem-sucedidas dos scripts criados pelo Mateus.

---

### Fase 5: Revisão Geral, Repositório & Submissão (**Responsáveis: MATEUS & LORENA — Categoria "Revisão"**)
* **Revisão Técnica Cruzada (Mateus & Lorena):** Lorena revisa os scripts Python e Mateus revisa o Relatório Técnico PDF.
* **Verificação do PDF:** Garantir que o Relatório Técnico respeite o limite estrito de até 5 páginas.
* **Controle de Versão (Mateus):** Atualização do `README.md` com instruções de uso e link público do repositório GitHub.
* **Empacotamento (Mateus):** Geração do arquivo único `.zip` contendo os scripts `.py` e o PDF.
* **Envio:** Submissão final na plataforma do professor até às 23h59 do dia 07/09/2026.

---

## 5. Organização Recomendada do Workspace

```text
Fundamentos-Hashing-Integridade/
│
├── docs/
│   ├── 2-Hashing_na_Cibersegurança.pdf
│   ├── Atividade_Pratica_Seguranca_Hashing.pdf
│   ├── Guia_Desenvolvimento_Hashing.md
│   └── Relatorio_Tecnico_Final.pdf
│
├── src/
│   ├── __init__.py
│   ├── verificador_integridade.py
│   ├── quebra_sem_salt.py
│   ├── cadastro_verificacao.py
│   ├── quebra_com_salt.py
│   └── detector_colisao.py
│
├── dados/
│   ├── hashes.txt
│   ├── hashes_com_salt.txt
│   ├── hashes_sem_salt.txt
│   ├── senhas_comuns.txt
│   └── usuarios.txt
│
├── tests/
│   └── test_scripts.py
│
└── README.md (contendo link do GitHub)
```
