# log_service.py
# Serviço de logging unificado para a aplicação LICITANET + OCR + OPENAI
# - Usa Loguru se disponível; caso contrário, cai para logging padrão
# - Expõe: get_logger(name), init_folders(), registrar_evento(...)

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# =========================
# Fallback: Loguru -> logging
# =========================
try:
    from loguru import logger as _logger  # type: ignore
    _USING_LOGURU = True
except ImportError:
    import logging
    _USING_LOGURU = False
    _logger = logging.get_Logger("app")
    _logger.setLevel(logging.INFO)
    # Handlers básicos
    _LOG_DIR_FALL = Path("logs")
    _LOG_DIR_FALL.mkdir(parents=True, exist_ok=True)
    _fh = logging.FileHandler(_LOG_DIR_FALL / "app.log", encoding="utf-8")
    _ch = logging.StreamHandler()
    _fmt = logging.Formatter(
        "%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d - %(message)s"
    )
    _fh.setFormatter(_fmt)
    _ch.setFormatter(_fmt)
    _logger.addHandler(_fh)
    _logger.addHandler(_ch)

# =========================
# Constantes e diretórios
# =========================
BASE_DIR = Path(".").resolve()
LOGS_DIR = BASE_DIR / "logs"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
EVIDENCES_DIR = ARTIFACTS_DIR / "evidences"

# =========================
# Configuração de log
# =========================
def _configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if _USING_LOGURU:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        # Remove handlers default do loguru para evitar logs duplicados
        _logger.remove()
        # INFO geral
        _logger.add(
            LOGS_DIR / "app.log",
            rotation="10 MB",
            retention="30 days",
            enqueue=True,
            format=log_format,
            level="INFO",
            encoding="utf-8",
        )
        # DEBUG detalhado
        _logger.add(
            LOGS_DIR / "debug.log",
            rotation="5 MB",
            retention="15 days",
            enqueue=True,
            format=log_format,
            level="DEBUG",
            encoding="utf-8",
        )


_configure_logging()

# =========================
# API pública
# =========================
def get_logger(name: str):
    """
    Retorna um logger para uso nos módulos.
    Com Loguru: retorna um logger "bindado" com o campo 'modulo'.
    Com logging: retorna logger convencional.
    """
    if _USING_LOGURU:
        return _logger.bind(modulo=name)
    else:
        # logging padrão
        import logging
        return logging.get_Logger(name)


def init_folders() -> dict:
    """
    Garante que todas as pastas da aplicação existam e retorna seus caminhos.
    """
    base_dirs = {
        "BASE_DIR": Path(".").resolve(),
        "INBOX_DIR": Path("inbox"),
        "PROCESSING_DIR": Path("processing"),
        "OUTBOX_DIR": Path("outbox"),
        "DONE_DIR": Path("done"),
        "ERROR_DIR": Path("error"),
        "EVID_OCR_DIR": Path("evidencias") / "ocr",
        "LOG_DIR": Path("logs"),
    }

    for key, path in base_dirs.items():
        path.mkdir(parents=True, exist_ok=True)

    _logger.info("Estrutura de diretórios inicializada com sucesso.")
    return {k: str(v) for k, v in base_dirs.items()}


def registrar_evento(
    etapa: str,
    mensagem: str,
    nivel: str = "INFO",
    *,
    job_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    salvar_evidencia_json: bool = False,
) -> Optional[Path]:
    """
    Helper simples para padronizar logs de etapas e, opcionalmente, salvar uma evidência JSON.

    Parâmetros:
        etapa: nome curto da etapa (ex.: 'WATCHER', 'OCR', 'OPENAI', 'SERPRO', 'RELATORIO')
        mensagem: texto do evento
        nivel: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
        job_id: id do job (opcional) para enriquecer o contexto
        extra: dict com dados adicionais (opcional)
        salvar_evidencia_json: se True, salva um JSON com o evento em artifacts/evidences/

    Retorna:
        Path do arquivo de evidência (se salvar_evidencia_json=True), caso contrário None.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    payload = {
        "timestamp": ts,
        "etapa": etapa,
        "mensagem": mensagem,
        "job_id": job_id,
        "extra": extra or {},
    }

    # Loga com nível apropriado
    if _USING_LOGURU:
        log_fn = {
            "DEBUG": _logger.debug,
            "INFO": _logger.info,
            "WARNING": _logger.warning,
            "ERROR": _logger.error,
            "CRITICAL": _logger.critical,
        }.get(nivel.upper(), _logger.info)
        log_fn(f"[{etapa}] {mensagem}", **({"job_id": job_id} if job_id else {}))
    else:
        import logging
        lvl = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }.get(nivel.upper(), logging.INFO)
        _logger.log(lvl, f"[{etapa}] {mensagem}")

    if not salvar_evidencia_json:
        return None

    # Salva evidência JSON padronizada
    EVIDENCES_DIR.mkdir(parents=True, exist_ok=True)
    fname = _make_evidence_filename(prefix=f"{etapa}_{nivel}", job_id=job_id, ext="json")
    fpath = EVIDENCES_DIR / fname
    with fpath.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return fpath


# =========================
# Utils internos
# =========================
def _make_evidence_filename(prefix: str, job_id: Optional[str], ext: str = "json") -> str:
    """
    Gera um nome de arquivo de evidência padronizado:
    YYYYMMDD_HHMMSS_mmm_PREFIX[_JOB]_evidence.ext
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    safe_prefix = _sanitize(prefix)
    suffix = f"_{_sanitize(job_id)}" if job_id else ""
    return f"{ts}_{safe_prefix}{suffix}_evidence.{ext}"


def _sanitize(s: Optional[str]) -> str:
    if not s:
        return "NA"
    return "".join(c for c in s if c.isalnum() or c in ("-", "_")).strip() or "NA"
