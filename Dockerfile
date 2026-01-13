# =====================================================
# 🐳 Dockerfile — LICITANET + OCR + OPENAI
# Baseado em Python 3.11 Slim
# =====================================================
FROM python:3.11-slim-bookworm

# Diretório de trabalho dentro do container
WORKDIR /app

# =====================================================
# 🔧 Configurações básicas
# =====================================================
# Evita cache pesado do pip e define variáveis de ambiente
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

# Instala dependências do sistema necessárias ao Tesseract, pdf2image e compilação
# Adicionado loop de retentativa para contornar falhas temporárias nos espelhos Debian
RUN apt-get update || apt-get update && \
    (apt-get install -y --fix-missing \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libzbar0 \
    libglib2.0-0 || \
    (sleep 5 && apt-get update && apt-get install -y --fix-missing \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libzbar0 \
    libglib2.0-0)) \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria diretórios vitais e garante permissão total
RUN mkdir -p /root/.cache/rapidocr /app/data /app/models && chmod -R 777 /root/.cache/rapidocr /app


# =====================================================
# 📦 Instala dependências Python
# =====================================================
# Copia apenas o requirements para cache otimizado
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- FIX: Pré-carregar modelos e ajustar permissões ---
# 1. Copia e roda script para baixar modelos agora (build time) em vez de na execução
COPY preload_models.py .
RUN python preload_models.py

# 2. (Removido chmod recursivo pois causa lentidão excessiva no build.
#     O container rodando como root já terá acesso aos arquivos criados aqui)
# -----------------------------------------------------

# =====================================================
# 📁 Copia todo o projeto
# =====================================================
COPY . .

# =====================================================
# 🌍 Exposição de portas
# =====================================================
# Streamlit utiliza por padrão a porta 8599
EXPOSE 8599

# =====================================================
# 🚀 Comando padrão de execução
# =====================================================
# Para rodar interface Streamlit (frontend):
CMD ["streamlit", "run", "main.py", "--server.port=8599", "--server.address=0.0.0.0", "--logger.level=debug"]


# Para rodar pipeline automático (modo produção):
#CMD ["python", "main.py"]


