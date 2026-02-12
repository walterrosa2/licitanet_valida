# Módulo 12 – Prompt Engineering & Python ↔ LLM

---

## 🎯 Objetivo da Aula
- Demonstrar, **na prática**, como o fluxo Licitanet integra **OCR**, **OpenAI**, e **SERPRO**.
- Aplicar técnicas avançadas de **engenharia de prompts**.
- Explorar **context coding**: manifest, roteamento e evidências.
- Discutir **limitações** (tokens, alucinações) e boas‑práticas.

---

## 📅 Agenda
1. Recap rápido dos módulos 1‑11
2. Visão geral da arquitetura (pipeline)
3. Engenharia de Prompt – como o código gera prompts
4. Integração Python ↔ OpenAI (API, .env, Loguru)
5. Context Coding – manifest, roteamento, pausas
6. Limitações & mitigação
7. Boas‑práticas recomendadas
8. Exercício prático + discussão

---

## 🔎 Recap curto (Módulos 1‑11)
- Fundamentos de IA e contabilidade
- OCR tradicional (Docling) e OCR especializado (CNH)
- Orquestração de pipelines e logging robusto
- **Módulo 12** foca na camada **LLM** que valida documentos.

---

## 🏗️ Visão de Alto Nível – Pipeline
![Pipeline Diagram](pipeline_diagram.png)

- **INBOX** → `watcher` detecta jobs → move para **PROCESSING**
- **OCR Router** decide entre **CNH OCR** ou **Docling/Tesseract**
- **OpenAI Validator** recebe prompt + payload (JSON)
- **SERPRO** enriquece dados de CNPJ
- **Relatório Final** consolida evidências e gera PDF/JSON

---

## 🧩 Fluxo de Dados – Passo‑a‑Passo
| Etapa | Código‑chave | O que acontece |
|------|--------------|----------------|
| 1️⃣ | `watcher.detect_and_move_jobs` | Detecta novos jobs, move para `processing`. |
| 2️⃣ | `ocr_router.executar_ocr` | Roteia cada arquivo → CNH OCR **ou** Docling/Tesseract. |
| 3️⃣ | `doc_verifier_agent.validar_documentos_openai` | Envia **prompt** + **payload** ao modelo OpenAI. |
| 4️⃣ | `consulta_serpro.consultar_cnpj` | Enriquecimento de dados externos. |
| 5️⃣ | `relatorio.gerar_relatorio_final` | Consolida evidências e gera PDF/JSON. |

---

## ✍️ Engenharia de Prompt – Implementação
- **Templates**: `PROMPT_PF_PATH` / `PROMPT_PJ_PATH` (arquivos Markdown). 
- **System message** = conteúdo do template → instruções de negócio.
- **User message** = JSON contendo:
  ```json
  {
    "job_id": "job_001",
    "tipo": "PJ",
    "modo": "padrao",
    "conteudo": "<texto extraído>"
  }
  ```
- **Modelo**: `gpt-4o-mini` (variável `OPENAI_MODEL`).
- **Temperatura**: `0.1` (determinístico).
- **Max tokens**: `4000` → evita respostas truncadas.
- **Versionamento**: nomear prompts como `prompt_pf_YYYYMMDD.md` e versionar no Git.

---

## 🐍 Integração Python ↔ OpenAI
| Item | Implementação |
|------|---------------|
| **Credenciais** | `.env` → `OPENAI_API_KEY` (carregado por `env_loader.get_client`). |
| **Cliente** | `OpenAI` wrapper (`get_client()`) – garante recarga da key a cada chamada. |
| **Chamada** | `client.chat.completions.create(model=…, messages=[…], temperature=0.1, max_tokens=4000)`. |
| **Tratamento de erro** | `try/except` → log via **Loguru**, retorno `status: "ERRO"`. |
| **Limite de tokens** | 4000 definido; fallback → dividir payload ou usar modo `comparativo` com resumo. |
| **Persistência** | Evidências de **entrada** e **saída** gravadas em `OUTBOX/ia/<job_id>_entrada_…json` e `_saida_…json`. |
| **Logging** | `LOGGER.bind(job_id=…, etapa="IA", evento="ENVIO")` → rastreio granular. |

---

## 📚 Context Coding – Codificando o Contexto
- **Manifest‑driven**: `manifest.json` descreve arquivos, tipos esperados, metadados. 
- **Roteamento** (`ocr_router.py`): decide CNH OCR vs. Docling/Tesseract usando `tipo_previsto` e heurística de nome. 
- **Pausa/Estabilidade**: `WAIT_STABILITY_SECONDS` (variável .env) → evita processar arquivos ainda em upload. 
- **Diretórios de trabalho**: criados por `init_folders()` → garante estrutura consistente (`INBOX`, `PROCESSING`, `DONE`, `ERROR`). 
- **Timestamp ISO** em todos os registros (`datetime.now().isoformat()`). 
- **Evidências**: arquivos Markdown para OCR, JSON para OpenAI, tudo versionado em `OUTBOX`. 

---

## ⚠️ Limitações & Mitigações
| Limitação | Impacto | Estratégia de mitigação |
|-----------|---------|--------------------------|
| **Token limit** (4000) | Respostas truncadas | Dividir conteúdo, usar modo `comparativo` apenas com resumos. |
| **Alucinações** | JSON inválido | Pós‑processamento `try json.loads`; fallback para `resposta_livre`. |
| **Rate‑limit / downtime** | Falha de chamada | Retry com back‑off exponencial (ex.: 3 tentativas). |
| **Qualidade do OCR** | Texto incompleto → prompt pobre | Fallback para Tesseract quando Docling < 200 chars. |
| **Segurança da chave** | Exposição acidental | `.env` + Loguru **não** grava a chave (mas grava máscara). |
| **Erros de caminho** | `FileNotFoundError` para prompts | Log de erro + fallback genérico (`Prompt não encontrado`). |

---

## ✅ Boas‑Práticas Recomendadas
- **Versionar prompts** e mantê‑los sob controle de versão (Git). 
- **Monitorar logs** (filtrar por `job_id`) para auditoria. 
- **Testar com jobs “dummy”** (`python -m doc_verifier_agent`). 
- **Separar ambientes**: `.env.dev` vs. `.env.prod`. 
- **Documentar limites** (tokens, tempo de execução) no README. 
- **Adicionar retry/circuit‑breaker** ao cliente OpenAI (ex.: `tenacity`). 

---

## 📌 Resumo & Próximos Passos
1. Revisar fluxo completo com foco em LLM. 
2. Implementar **retry** e **circuit‑breaker** (atividade opcional). 
3. Preparar exercício prático: criar novo prompt e validar via API. 
4. Discutir dúvidas e planejar o módulo 13 (automação avançada). 

---

## ❓ Perguntas & Discussão
- Alguma parte do fluxo ficou confusa?
- Quer aprofundar algum detalhe (ex.: tratamento de erros, versionamento de prompts)?
- Próximo workshop: **Automação avançada com Streamlit + background workers**.

---

*Design notes (para quem for importar no gamma.app):* 
- **Tema escuro** com gradiente **teal → purple** (glassmorphism). 
- Fonte sugerida: **"Inter"** (Google Fonts). 
- Use **micro‑animações** nos blocos de código (fade‑in) e nas setas do diagrama. 
- Cada slide tem um **título em negrito** e **ícones** (ex.: 🎯, 📅, 🏗️). 
- Imagem do pipeline já está incluída no slide 4.
