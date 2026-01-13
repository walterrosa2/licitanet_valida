# watcher.py
# Monitoramento + Orquestração do pipeline LICITANET + OCR + OPENAI (v3)

from __future__ import annotations
import os
import time
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Iterable

from log_service import get_logger, init_folders, registrar_evento, safe_mkdir
from manifest_loader import load_manifest
from ocr_router import executar_ocr
from doc_verifier_agent import validar_documentos_openai
from consulta_serpro import consultar_cnpj
from relatorio import gerar_relatorio_final

LOGGER = get_logger("watcher")
LOGGER.info(f"watcher.py carregado de: {__file__}")

DIRS = init_folders()

SLEEP_INTERVAL = int(os.getenv("WATCHER_SLEEP_SECONDS", "5"))
WAIT_STABILITY_SECONDS = int(os.getenv("WAIT_STABILITY_SECONDS", "5"))  # .env.txt já sugere 5

# -----------------------------------------------------------------------------
# Utils de detecção/movimentação
# -----------------------------------------------------------------------------
def _iter_inbox_job_dirs() -> Iterable[Path]:
    """Varre recursivamente /inbox e retorna pastas que possuem manifest.json."""
    inbox_root = Path(DIRS["INBOX_DIR"])
    if not inbox_root.exists():
        return []
    for p in inbox_root.rglob("*/"):
        p = Path(p)
        if not p.is_dir():
            continue
        if (p / "manifest.json").exists():
            # Garante que é um <job_id> (último nível) e não apenas o diretório de data
            yield p

def _is_upload_in_progress(job_dir: Path) -> bool:
    """Heurística simples: se existir qualquer arquivo *.part, ainda está em upload."""
    for item in job_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() == ".part":
            return True
    return False

def _move_job_to_processing(inbox_job_dir: Path) -> Path:
    """Move /inbox/.../<job_id>/ para /processing/<job_id>/ (rename atômico)."""
    job_id = inbox_job_dir.name
    dest = Path(DIRS["PROCESSING_DIR"]) / job_id
    if dest.exists():
        shutil.rmtree(dest)
    safe_mkdir(dest.parent)
    # move a pasta do job inteira
    shutil.move(str(inbox_job_dir), str(dest))
    return dest

def _move_processing_to_done(job_id: str):
    src = Path(DIRS["PROCESSING_DIR"]) / job_id
    dest = Path(DIRS["DONE_DIR"]) / job_id
    if dest.exists():
        shutil.rmtree(dest)
    if src.exists():
        shutil.move(str(src), str(dest))

def _move_processing_to_error(job_id: str):
    src = Path(DIRS["PROCESSING_DIR"]) / job_id
    dest = Path(DIRS["ERROR_DIR"]) / job_id
    if dest.exists():
        shutil.rmtree(dest)
    if src.exists():
        shutil.move(str(src), str(dest))

# -----------------------------------------------------------------------------
# Integração ReceitaWS/SERPRO – staging do manifest
# -----------------------------------------------------------------------------
def _stage_manifest_for_serpro(job_id: str, manifest: Dict[str, Any]) -> Path:
    """
    Grava uma cópia do manifest para consumo do módulo consulta_serpro.py em:
    /outbox/<job_id>/serpro/manifest_for_serpro.json
    """
    serpro_dir = Path(DIRS["OUTBOX_DIR"]) / job_id / "serpro"
    safe_mkdir(serpro_dir)
    queued = serpro_dir / "manifest_for_serpro.json"

    with queued.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, default=str)

    LOGGER.info(f"[{job_id}] Manifest staged para ReceitaWS: {queued.as_posix()}")
    return queued

# -----------------------------------------------------------------------------
# Pipeline de um job
# -----------------------------------------------------------------------------
def process_job(inbox_job_dir: Path):
    """Executa o pipeline completo para um único job."""
    job_id = inbox_job_dir.name
    registrar_evento("WATCHER", f"Novo job detectado em inbox: {inbox_job_dir.as_posix()}", job_id=job_id)

    # Aguarda estabilidade básica de upload (.part sumir)
    if _is_upload_in_progress(inbox_job_dir):
        LOGGER.warning(f"[{job_id}] Upload em andamento (.part detectado). Aguardando {WAIT_STABILITY_SECONDS}s…")
        time.sleep(WAIT_STABILITY_SECONDS)
        if _is_upload_in_progress(inbox_job_dir):
            LOGGER.warning(f"[{job_id}] Upload ainda não estabilizado. Pular nesta iteração.")
            return

    # Move para /processing/<job_id>/
    processing_dir = _move_job_to_processing(inbox_job_dir)
    registrar_evento("WATCHER", f"Job movido para processing: {processing_dir.as_posix()}", job_id=job_id)

    try:
        # 1) Carrega e valida manifest
        manifest: Dict[str, Any] = load_manifest(processing_dir, strict_files=True)
        # Airbag de compatibilidade com versões antigas:
        manifest_data = manifest
        if manifest.get("job_id") != job_id:
            LOGGER.warning(f"[{job_id}] job_id no manifest difere do nome da pasta. Prosseguindo assim mesmo.")

        # 2) OCR/Docling
        LOGGER.info(f"[{job_id}] Iniciando OCR/Docling…")
        ocr_result = executar_ocr(job_id, manifest)
        LOGGER.info(f"[{job_id}] OCR/Docling concluído: {ocr_result.get('status')}")

        # 3) IA Validador 1
        LOGGER.info(f"[{job_id}] Iniciando IA Validador 1…")
        ia1_result = validar_documentos_openai(job_id, ocr_result.get("dados_extraidos", ""), manifest, modo="padrao")
        LOGGER.info(f"[{job_id}] IA1 concluída: {ia1_result.get('status')}")

        # 4) ReceitaWS/SERPRO – stage do manifest e consulta
        LOGGER.info(f"[{job_id}] Consultando dados ReceitaWS…")
        # antes de consultar o SERPRO:
        _stage_manifest_for_serpro(job_id, manifest)

        serpro_result = consultar_cnpj(manifest)

        LOGGER.info(f"[{job_id}] ReceitaWS concluída: {serpro_result.get('status')}")

        # 5) IA Validador 2 (comparativa)
        LOGGER.info(f"[{job_id}] Iniciando IA Validador 2 (comparativa)…")
        entrada_ia2 = {
            "dados_ocr": ocr_result.get("dados_extraidos", ""),
            "dados_serpro": serpro_result.get("dados", {}),
            "resultado_ia1": ia1_result.get("resultado", {}),
        }
        ia2_result = validar_documentos_openai(job_id, json.dumps(entrada_ia2, ensure_ascii=False), manifest, modo="comparativo")
        LOGGER.info(f"[{job_id}] IA2 concluída: {ia2_result.get('status')}")

        # 6) Relatórios finais
        LOGGER.info(f"[{job_id}] Gerando relatório final…")
        gerar_relatorio_final(job_id, manifest, ocr_result, ia1_result, serpro_result, ia2_result)
        LOGGER.info(f"[{job_id}] Relatório final gerado.")

        # 7) Done
        _move_processing_to_done(job_id)
        registrar_evento("WATCHER", "Pipeline concluído com sucesso", "INFO", job_id=job_id)

    except Exception as e:
        LOGGER.exception(f"[{job_id}] Erro durante o processamento do job: {e}")
        _move_processing_to_error(job_id)
        registrar_evento(job_id=job_id, etapa="WATCHER", mensagem=f"Pipeline falhou: {e}", nivel="erro")


# -----------------------------------------------------------------------------
# Loop principal
# -----------------------------------------------------------------------------
def detect_and_move_jobs(run_once: bool = False):
    LOGGER.info("Iniciando monitoramento do diretório /inbox …")
    while True:
        jobs = list(_iter_inbox_job_dirs())
        if jobs:
            LOGGER.info(f"{len(jobs)} job(s) detectado(s) em /inbox.")
            for job_dir in jobs:
                process_job(job_dir)
        else:
            LOGGER.debug("Nenhum job novo detectado.")

        if run_once:
            break
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    detect_and_move_jobs(run_once=False)
