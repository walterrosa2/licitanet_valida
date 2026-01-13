# ocr_router.py
# Roteador de OCR: Despacha para CNH OCR ou Extrator Genérico (Docling)
# Substitui o ponto de entrada antigo: extrator_docling.executar_ocr

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from log_service import get_logger, init_folders, safe_mkdir
from cnh_ocr import process_cnh
from extrator_docling import extrair_com_docling, extrair_com_tesseract, localizar_arquivo

LOGGER = get_logger("ocr_router")
DIRS = init_folders()

def executar_ocr(job_id: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Controlador principal de OCR.
    Itera sobre os arquivos do manifest e decide qual extrator usar.
    """
    evid_dir = Path(DIRS["EVID_OCR_DIR"]) / job_id
    safe_mkdir(evid_dir)
    
    resultados: List[Dict[str, Any]] = []
    texto_consolidado = ""
    
    LOGGER.bind(job_id=job_id, etapa="OCR_ROUTER").info(f"Iniciando OCR para {len(manifest['arquivos'])} arquivos.")

    for arquivo in manifest["arquivos"]:
        nome = arquivo["nome"]
        tipo_previsto = arquivo.get("tipo_previsto", "").upper()
        caminho_pdf = localizar_arquivo(job_id, nome)
        
        if not caminho_pdf or not os.path.exists(caminho_pdf):
            LOGGER.bind(job_id=job_id, arquivo=nome, status="ERRO").error("Arquivo não encontrado.")
            continue
            
        # --- ROTEAMENTO ---
        # Verifica se é CNH pelo tipo OU pelo nome do arquivo (fallback)
        is_cnh = (tipo_previsto in ["CNH", "DOC_IDENT_CNH", "CNH_OFICIAL"])
        if not is_cnh:
            nome_lower = nome.lower()
            if "cnh" in nome_lower or "habilitacao" in nome_lower:
                is_cnh = True
                LOGGER.info(f"Detectado CNH pelo nome do arquivo: {nome}")

        if is_cnh:
            # Rota Especializada: CNH
            LOGGER.info(f"Roteando {nome} para CNH OCR.")
            try:
                res = process_cnh(caminho_pdf, job_id, arquivo["id"], manifest)
                
                # Adapta retorno do process_cnh para lista de resultados
                resultados.append({
                    "arquivo": nome,
                    "metodo": "CNH_OCR",
                    "evidencia": res["evidencias"]["markdown"],
                    "status": "OK",
                    "tamanho_texto": len(res.get("conteudo_markdown", "")),
                    "cnh_metadata": res.get("cnh_json")
                })
                texto_consolidado += f"\n\n# {nome} (CNH OCR)\n{res.get('conteudo_markdown', '')}"
                
            except Exception as e:
                LOGGER.exception(f"Erro no CNH OCR para {nome}: {e}")
                resultados.append({"arquivo": nome, "status": "ERRO", "erro": str(e)})

        else:
            # Rota Padrão: Docling + Tesseract Fallback
            LOGGER.info(f"Roteando {nome} para Pipeline Padrão (Docling).")
            try:
                # Lógica replicada de extrator_docling.py
                texto_docling = extrair_com_docling(caminho_pdf)
                if texto_docling and len(texto_docling.strip()) > 200:
                    texto_extraido = texto_docling
                    metodo = "Docling"
                else:
                    texto_ocr = extrair_com_tesseract(caminho_pdf)
                    texto_extraido = texto_ocr
                    metodo = "Tesseract"
                
                # Salvar Evidência
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
                
            except Exception as e:
                LOGGER.exception(f"Erro no OCR Padrão para {nome}: {e}")
                resultados.append({"arquivo": nome, "status": "ERRO", "erro": str(e)})

    # Resumo final compatível com extrator_docling.py
    resumo = {
        "status": "OK" if all(r.get("status") == "OK" for r in resultados) else "ERRO",
        "job_id": job_id,
        "evidencias_dir": str(evid_dir),
        "dados_extraidos": texto_consolidado,
        "arquivos": resultados,
        "data_execucao": datetime.now().isoformat()
    }
    
    return resumo
