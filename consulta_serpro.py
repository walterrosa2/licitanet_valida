# consulta_serpro.py — versão 100% ReceitaWS (fonte única)
# Mantém a função pública consultar_cnpj(manifest) para compatibilidade com o pipeline.

import os
import re
import json
import time
import inspect
from datetime import datetime
from pathlib import Path
from typing import Tuple

import httpx  # cliente HTTP usado em outras apps suas

from log_service import get_logger, init_folders

LOGGER = get_logger("receitaws_agent")
DIRS = init_folders()

LOGGER.info("ReceitaWS MODE ATIVO — consulta_serpro.py (build 2025-11-05) | file=%s", __file__)


# ===== Config por .env =====
RECEITAWS_BASE_URL = os.getenv("RECEITAWS_BASE_URL", "https://www.receitaws.com.br/v1/cnpj/")
RECEITAWS_TOKEN = os.getenv("RECEITAWS_TOKEN", "").strip()
RECEITAWS_TIMEOUT = float(os.getenv("RECEITAWS_TIMEOUT", "20"))
RECEITAWS_RETRIES = int(os.getenv("RECEITAWS_RETRIES", "3"))
RECEITAWS_BACKOFF = float(os.getenv("RECEITAWS_BACKOFF", "1.5"))  # fator exponencial


from typing import Tuple

def _serpro_manifest_paths(job_id: str) -> Tuple[Path, Path]:
    """
    Retorna (path_queued, path_done) dentro de outbox/<job_id>/serpro/.
    """
    serpro_dir = Path(DIRS["OUTBOX_DIR"]) / job_id / "serpro"
    serpro_dir.mkdir(parents=True, exist_ok=True)
    queued = serpro_dir / "manifest_for_serpro.json"
    done = serpro_dir / "manifest_for_serpro.done.json"
    return queued, done

def _maybe_load_manifest_from_queue(job_id: str) -> dict | None:
    """
    Se existir a cópia staged do manifest (manifest_for_serpro.json), carrega e retorna.
    Caso contrário, retorna None.
    """
    queued, _ = _serpro_manifest_paths(job_id)
    if queued.exists():
        try:
            with queued.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            LOGGER.warning(f"[RECEITAWS] Falha ao ler manifest staged: {queued} — {e}")
    return None

def _mark_manifest_done(job_id: str) -> None:
    """
    Marca a cópia staged do manifest como 'done' (rename atômico).
    """
    queued, done = _serpro_manifest_paths(job_id)
    if queued.exists():
        try:
            if done.exists():
                done.unlink()  # evita colidir com leftovers
            queued.rename(done)
            LOGGER.info(f"[RECEITAWS] Manifesto marcado como done: {done}")
        except Exception as e:
            LOGGER.warning(f"[RECEITAWS] Não foi possível marcar manifest como done: {e}")



# ===== Utils =====
def _limpar_cnpj(v) -> str:
    s = "" if v is None else str(v)
    return re.sub(r"\D", "", s)

def _get_cnpj_from_manifest(manifest: dict) -> str:
    cnpj = _limpar_cnpj(manifest.get("fornecedor_id"))
    if cnpj:
        return cnpj
    cnpj = _limpar_cnpj((manifest.get("contexto") or {}).get("cnpj"))
    if cnpj:
        return cnpj
    return _limpar_cnpj(manifest.get("cnpj"))

def _evid_paths(job_id: str) -> Tuple[Path, Path, Path]:
    """
    Mantemos a pasta 'serpro' por compatibilidade externa:
    outbox/<job_id>/serpro/{entrada_*.json, saida_*.json}
    """
    evid_dir = Path(DIRS["OUTBOX_DIR"]) / job_id / "serpro"
    evid_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    entrada = evid_dir / f"{job_id}_entrada_receitaws_{ts}.json"
    saida = evid_dir / f"{job_id}_saida_receitaws_{ts}.json"
    return evid_dir, entrada, saida

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== Camada ReceitaWS (fonte única) =====
def _consultar_receitaws(cnpj: str, entrada_path: Path, saida_path: Path) -> dict:
    """
    Consulta a ReceitaWS com retries e backoff exponencial.
    Nunca levanta exceção para o pipeline — sempre retorna dict padronizado.
    """
    # Monta URL com token opcional (?token=...)
    url = f"{RECEITAWS_BASE_URL}{cnpj}"
    if RECEITAWS_TOKEN:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}token={RECEITAWS_TOKEN}"

    entrada = {
        "fonte": "RECEITAWS",
        "cnpj": cnpj,
        "url": url,
        "timeout": RECEITAWS_TIMEOUT,
        "retries": RECEITAWS_RETRIES,
        "backoff": RECEITAWS_BACKOFF,
        "tem_token": bool(RECEITAWS_TOKEN),
    }
    _save_json(entrada_path, entrada)

    attempt = 0
    while True:
        attempt += 1
        try:
            with httpx.Client(timeout=RECEITAWS_TIMEOUT) as client:
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json()

            # ReceitaWS pode devolver {"status": "ERROR", "message": "..."} em casos de limite/espera
            if isinstance(data, dict) and data.get("status") == "ERROR":
                msg = data.get("message", "Erro ReceitaWS")
                LOGGER.warning(f"[RECEITAWS][{cnpj}] status=ERROR: {msg}")
                # Se for erro que pode se resolver sozinho (p.ex. “pode realizar nova consulta em X segundos”),
                # respeitamos retries. Caso já excedeu retries, retorna erro padronizado.
                if attempt >= RECEITAWS_RETRIES:
                    return {"status": "ERRO_HTTP", "erro": msg, "dados": {}, "serpro_disponivel": False}
            else:
                # OK
                _save_json(saida_path, data)
                return {"status": "OK", "dados": data, "serpro_disponivel": False}

        except httpx.TimeoutException as e:
            LOGGER.warning(f"[RECEITAWS][{cnpj}] Timeout (tentativa {attempt}/{RECEITAWS_RETRIES}): {e}")
            if attempt >= RECEITAWS_RETRIES:
                return {"status": "ERRO_TIMEOUT", "erro": str(e), "dados": {}, "serpro_disponivel": False}

        except httpx.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            LOGGER.warning(f"[RECEITAWS][{cnpj}] HTTP {status} (tentativa {attempt}/{RECEITAWS_RETRIES}): {e}")
            # 4xx (exceto 429) dificilmente resolvem com retry; 5xx/429 podem ser transientes
            if attempt >= RECEITAWS_RETRIES or (status and status < 500 and status != 429):
                return {"status": "ERRO_HTTP", "erro": f"HTTP {status}", "dados": {}, "serpro_disponivel": False}

        except Exception as e:
            LOGGER.exception(f"[RECEITAWS][{cnpj}] Erro inesperado: {e}")
            return {"status": "ERRO", "erro": str(e), "dados": {}, "serpro_disponivel": False}

        # backoff exponencial com teto (para não travar por muito tempo)
        sleep_s = min(RECEITAWS_BACKOFF ** attempt, 15)
        time.sleep(sleep_s)


# ===== API pública do módulo (usada no pipeline) =====
def consultar_cnpj(manifest: dict) -> dict:
    job_id = manifest.get("job_id", "sem_id")

    # Se existir uma cópia staged do manifest, ela tem prioridade
    staged = _maybe_load_manifest_from_queue(job_id)
    if staged:
        manifest = staged
        LOGGER.debug({"dbg": "receitaws_manifest_source", "source": "staged_copy"})
    else:
        LOGGER.debug({"dbg": "receitaws_manifest_source", "source": "in_memory"})
    """
    Consulta cadastral via ReceitaWS (fonte única).
    Mantém o contrato de retorno esperado pelo pipeline:
    {
      "status": "OK|ERRO|ERRO_TIMEOUT|ERRO_HTTP",
      "job_id": "...",
      "cnpj": "...",
      "dados": {...},                      # sempre dict
      "serpro_disponivel": False,         # mantido por compatibilidade a IA2/prompts
      "arquivos_evidencia": {"entrada": "...", "saida": "..."},
      "data_execucao": "..."
    }
    """


    caller = inspect.stack()[1]
    LOGGER.debug({
        "dbg": "consulta_cnpj_manifest_view",
        "caller_file": caller.filename,
        "caller_line": caller.lineno,
        "manifest_keys": list(manifest.keys()),
        "job_id": manifest.get("job_id"),
        "fornecedor_id": (str(manifest.get("fornecedor_id"))[:8] if manifest.get("fornecedor_id") else None),
        "contexto_has": isinstance(manifest.get("contexto"), dict),
        "contexto_cnpj": (manifest.get("contexto") or {}).get("cnpj"),
        "cnpj_root": manifest.get("cnpj"),
    })

    LOGGER.debug({
        "dbg": "consulta_cnpj_manifest_view",
        "manifest_keys": list(manifest.keys()),
        "fornecedor_id": str(manifest.get("fornecedor_id"))[:6] if manifest.get("fornecedor_id") else None,
        "contexto_has": isinstance(manifest.get("contexto"), dict),
        "contexto_cnpj": (manifest.get("contexto") or {}).get("cnpj"),
        "cnpj_root": manifest.get("cnpj"),
    })

    job_id = manifest.get("job_id", "sem_id")
    cnpj = _get_cnpj_from_manifest(manifest)

    evid_dir, entrada_path, saida_path = _evid_paths(job_id)

    if not cnpj:
        msg = "CNPJ ausente — esperado em fornecedor_id, contexto.cnpj ou cnpj (raiz)."
        # salva snapshot do manifest visto por ESTE módulo
        evid_dir, entrada_path, _ = _evid_paths(manifest.get("job_id","sem_id"))
        _save_json(entrada_path.with_name(entrada_path.name.replace("entrada","entrada_manifest_snapshot")),
                {"erro": msg, "manifest_snapshot": manifest})
        LOGGER.error(msg)
        return {
            "status": "ERRO",
            "job_id": job_id,
            "cnpj": "",
            "dados": {},
            "serpro_disponivel": False,
            "arquivos_evidencia": {"entrada": str(entrada_path)},
            "data_execucao": datetime.now().isoformat()
        }


    res = _consultar_receitaws(cnpj, entrada_path, saida_path)

    retorno = {
        "status": res.get("status", "ERRO"),
        "job_id": job_id,
        "cnpj": cnpj,
        "dados": res.get("dados", {}) or {},
        "serpro_disponivel": False,  # fixo (compatibilidade)
        "arquivos_evidencia": {},
        "data_execucao": datetime.now().isoformat()
    }
    if entrada_path.exists():
        retorno["arquivos_evidencia"]["entrada"] = str(entrada_path)
    if saida_path.exists() and retorno["status"] == "OK":
        retorno["arquivos_evidencia"]["saida"] = str(saida_path)
    _mark_manifest_done(job_id)           # ← E AQUI (antes do return)
    return retorno


# ===== Teste isolado =====
if __name__ == "__main__":
    manifest_teste = {
        "job_id": "job_teste",
        "perfil_validacao": "PJ",
        "fornecedor_id": "22157088000192"  # BMF TURISMO LTDA
    }
    r = consultar_cnpj(manifest_teste)
    print(json.dumps(r, ensure_ascii=False, indent=2))
