"""
extrator_docling.py
--------------------
Responsável pela conversão de PDFs e imagens em texto legível.
Fluxo:
1. Detecta tipo de documento (texto x imagem)
2. Extrai conteúdo com Docling (texto nativo)
3. Fallback OCR com Tesseract se o Docling não conseguir extrair texto útil
4. Salva resultados em evidencias/ocr/<job_id>/
5. Retorna dicionário padronizado para uso pelo watcher

Dependências:
- docling
- pdfplumber
- pytesseract
- pdf2image
- pillow
- loguru
"""

import os
import io
from pathlib import Path
from log_service import get_logger, init_folders, safe_mkdir
from datetime import datetime
from typing import Dict, Any, List

# OCR libs
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Docling (parser PDF to Markdown)
from docling.document_converter import DocumentConverter

LOGGER = get_logger("ocr_router")
DIRS = init_folders()

def executar_ocr(job_id: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa OCR/Docling em todos os arquivos listados no manifest.
    Retorna dicionário com status, dados extraídos e paths das evidências.
    """
    evid_dir = Path(DIRS["EVID_OCR_DIR"]) / job_id
    safe_mkdir(evid_dir)

    resultados: List[Dict[str, Any]] = []
    texto_consolidado = ""

    for arquivo in manifest["arquivos"]:
        nome = arquivo["nome"]
        caminho_pdf = localizar_arquivo(job_id, nome)

        if not caminho_pdf or not os.path.exists(caminho_pdf):
            LOGGER.bind(job_id=job_id, etapa="OCR", arquivo=nome, status="ERRO").error(f"Arquivo não encontrado: {nome}")
            continue

        LOGGER.bind(job_id=job_id, etapa="OCR", arquivo=nome, status="INICIO").info(f"Iniciando extração de {nome}")

        try:
            texto_docling = extrair_com_docling(caminho_pdf)
            if texto_docling and len(texto_docling.strip()) > 200:
                texto_extraido = texto_docling
                metodo = "Docling"
            else:
                texto_ocr = extrair_com_tesseract(caminho_pdf)
                texto_extraido = texto_ocr
                metodo = "Tesseract"

            # Salva evidência em Markdown
            markdown_path = evid_dir / f"{Path(nome).stem}_{metodo}.md"
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(texto_extraido)

            resultados.append({
                "arquivo": nome,
                "metodo": metodo,
                "evidencia": str(markdown_path),
                "status": "OK",
                "tamanho_texto": len(texto_extraido)
            })

            texto_consolidado += f"\n\n# {nome} ({metodo})\n{texto_extraido}"
            LOGGER.bind(job_id=job_id, etapa="OCR", arquivo=nome, status="OK").info(f"Extração concluída: {nome} via {metodo}")

        except Exception as e:
            LOGGER.bind(job_id=job_id, etapa="OCR", arquivo=nome, status="ERRO").exception(f"Erro ao processar {nome}: {e}")
            resultados.append({
                "arquivo": nome,
                "metodo": None,
                "status": "ERRO",
                "erro": str(e)
            })

    resumo = {
        "status": "OK" if all(r["status"] == "OK" for r in resultados) else "ERRO",
        "job_id": job_id,
        "evidencias_dir": str(evid_dir),
        "dados_extraidos": texto_consolidado,
        "arquivos": resultados,
        "data_execucao": datetime.now().isoformat()
    }

    return resumo

def localizar_arquivo(job_id: str, nome_arquivo: str) -> str:
    """Busca o arquivo PDF dentro da pasta /processing/<job_id>/"""
    base_path = Path(DIRS["PROCESSING_DIR"]) / job_id
    for root, _, files in os.walk(base_path):
        if nome_arquivo in files:
            return str(Path(root) / nome_arquivo)
    return ""

def extrair_com_docling(path_pdf: str) -> str:
    """Tenta converter PDF para texto via Docling."""
    try:
        converter = DocumentConverter()
        result = converter.convert(path_pdf)
        return result.document.export_to_markdown()
    except Exception as e:
        LOGGER.bind(arquivo=path_pdf, evento="DOCLING", status="ERRO").warning(f"Docling falhou: {e}")
        return ""

def extrair_com_tesseract(path_pdf: str) -> str:
    """Converte PDF para imagem e aplica OCR com Tesseract."""
    texto_final = ""
    try:
        images = convert_from_path(path_pdf, dpi=300)
        for i, img in enumerate(images):
            texto = pytesseract.image_to_string(img, lang="por+eng", config="--psm 6")
            texto_final += f"\n\n--- Página {i+1} ---\n{texto}"
        return texto_final
    except Exception as e:
        LOGGER.bind(arquivo=path_pdf, evento="TESSERACT", status="ERRO").warning(f"Erro no OCR Tesseract: {e}")
        return texto_final
