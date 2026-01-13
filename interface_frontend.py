"""
interface_frontend.py
----------------------
Interface Streamlit da aplicação LICITANET + OCR + OPENAI.

Funcionalidades:
1. Upload de arquivos e manifest.json
2. Monitoramento dos jobs e status (inbox, processing, done, error)
3. Reprocessamento manual de jobs com erro
4. Exibição de relatórios (resumo executivo e checklist)
"""

import streamlit as st
import os
import json
from pathlib import Path
from log_service import init_folders, safe_mkdir
from main import executar_pipeline_manual

# Inicializa estrutura
DIRS = init_folders()

# === Configurações de página ===
st.set_page_config(
    page_title="Licitanet + OCR + OpenAI",
    layout="wide",
    page_icon="📄"
)

st.title("📑 Licitanet + OCR + OpenAI — Verificação Documental Automatizada")
st.markdown("---")

# === Abas ===
aba = st.sidebar.radio(
    "📂 Escolha a seção:",
    ["Upload de Job", "Monitoramento", "Reprocessamento", "Relatórios"]
)

# ============================================
# 1️⃣ UPLOAD DE NOVO JOB
# ============================================
if aba == "Upload de Job":
    st.header("📤 Enviar novo job para processamento")

    job_id = st.text_input("ID do Job (ex: job_001)")
    manifest_file = st.file_uploader("Envie o arquivo manifest.json", type=["json"])
    arquivos = st.file_uploader(
        "Envie os arquivos PDF associados", type=["pdf"], accept_multiple_files=True
    )

    if st.button("🚀 Enviar para processamento"):
        if not job_id or not manifest_file or not arquivos:
            st.error("Preencha o ID do job, o manifest e ao menos um arquivo PDF.")
        else:
            job_dir = Path(DIRS["INBOX_DIR"]) / job_id
            safe_mkdir(job_dir)

            # Salva manifest
            manifest_path = job_dir / "manifest.json"
            with open(manifest_path, "wb") as f:
                f.write(manifest_file.getbuffer())

            # Salva PDFs
            for file in arquivos:
                file_path = job_dir / file.name
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

            st.success(f"✅ Job {job_id} enviado com sucesso para /inbox/.")
            st.info("O watcher processará o job automaticamente nos próximos segundos.")

# ============================================
# 2️⃣ MONITORAMENTO DE JOBS
# ============================================
elif aba == "Monitoramento":
    st.header("🕵️ Monitoramento de Jobs")
    col1, col2, col3, col4 = st.columns(4)

    def listar_jobs(pasta):
        return [p.name for p in Path(pasta).iterdir() if p.is_dir()]

    jobs_inbox = listar_jobs(DIRS["INBOX_DIR"])
    jobs_processing = listar_jobs(DIRS["PROCESSING_DIR"])
    jobs_done = listar_jobs(DIRS["DONE_DIR"])
    jobs_error = listar_jobs(DIRS["ERROR_DIR"])

    col1.metric("🧾 Inbox", len(jobs_inbox))
    col2.metric("⚙️ Processing", len(jobs_processing))
    col3.metric("✅ Done", len(jobs_done))
    col4.metric("❌ Error", len(jobs_error))

    st.markdown("### 🔍 Detalhamento de jobs por status")

    with st.expander("📥 Jobs em Inbox"):
        st.write(jobs_inbox or "Nenhum job pendente.")

    with st.expander("⚙️ Jobs em Processamento"):
        st.write(jobs_processing or "Nenhum job em execução.")

    with st.expander("✅ Jobs Concluídos"):
        st.write(jobs_done or "Nenhum job finalizado.")

    with st.expander("❌ Jobs com Erro"):
        st.write(jobs_error or "Nenhum job com falha.")

# ============================================
# 3️⃣ REPROCESSAMENTO MANUAL
# ============================================
elif aba == "Reprocessamento":
    st.header("♻️ Reprocessar job com erro")

    jobs_error = [p.name for p in Path(DIRS["ERROR_DIR"]).iterdir() if p.is_dir()]

    if not jobs_error:
        st.info("Nenhum job com erro disponível para reprocessamento.")
    else:
        job_selecionado = st.selectbox("Selecione um job:", jobs_error)
        if st.button("🔁 Reprocessar agora"):
            st.info(f"Reprocessando job {job_selecionado}...")
            try:
                executar_pipeline_manual(job_selecionado)
                st.success(f"✅ Job {job_selecionado} reprocessado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao reprocessar job: {e}")

# ============================================
# 4️⃣ VISUALIZAÇÃO DE RELATÓRIOS
# ============================================
elif aba == "Relatórios":
    st.header("📊 Relatórios de Jobs Concluídos")

    jobs_done = [p.name for p in Path(DIRS["DONE_DIR"]).iterdir() if p.is_dir()]
    if not jobs_done:
        st.info("Nenhum job concluído encontrado.")
    else:
        job_selecionado = st.selectbox("Selecione um job:", jobs_done)
        resultado_dir = Path(DIRS["OUTBOX_DIR"]) / job_selecionado / "resultado"

        resumo_path = resultado_dir / "resumo_executivo.md"
        checklist_path = resultado_dir / "checklist_validacao.md"

        if resumo_path.exists():
            with open(resumo_path, "r", encoding="utf-8") as f:
                resumo = f.read()
            st.subheader("📘 Resumo Executivo")
            st.markdown(resumo)

        if checklist_path.exists():
            with open(checklist_path, "r", encoding="utf-8") as f:
                checklist = f.read()
            st.subheader("📋 Checklist de Validação")
            st.markdown(checklist)
