# manifest_loader.py
# v3 — alinhado à "Licitanet + OCR + OpenAI — Documentação Técnica & Funcional (v3)"
# Responsável por: ler, validar e normalizar o manifest.json de cada job.

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from log_service import get_logger
from jsonschema import Draft202012Validator, ValidationError

# Logger unificado do projeto
LOGGER = get_logger("manifest_loader")


# Validação de schema
from jsonschema import Draft202012Validator, ValidationError


# ==========================
# SCHEMA v3 (fallback interno)
# ==========================
_SCHEMA_V3_FALLBACK: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["job_id", "fornecedor_id", "arquivos", "perfil_validacao"],
    "additionalProperties": False,
    "properties": {
        "job_id": {"type": "string", "minLength": 8},
        "fornecedor_id": {"type": "string"},
        "perfil_validacao": {"type": "string", "enum": ["PF", "PJ"]},
        "subperfil_pf": {
            "type": ["string", "null"],
            "enum": ["PF_Pura", "PF_EI", None],
            "default": None,
        },
        "contexto": {"type": "object", "additionalProperties": True},
        "reprocessar": {"type": "boolean", "default": False},
        "reprocess_scope": {
            "type": "string",
            "enum": ["PDF", "OPENAI", "FULL", "AUTO_MANIFEST"],
            "default": "AUTO_MANIFEST",
        },
        "arquivos": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "nome", "paginas", "hash"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "nome": {"type": "string"},
                    "tipo_previsto": {"type": "string"},
                    "origem": {"type": "string"},
                    "paginas": {"type": "integer", "minimum": 1},
                    "hash": {"type": "string"},
                    "legibilidade_score": {
                        "type": ["number", "null"],
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "opcional": {"type": "boolean", "default": False},
                },
            },
        },
        "metadados": {"type": "object", "additionalProperties": True},
    },
}


def _load_external_schema_if_exists() -> Dict[str, Any]:
    """
    Se existir ./schemas/manifest_v3.json, usa-o como schema.
    Caso contrário, usa o fallback interno.
    """
    candidate = Path("schemas") / "manifest_v3.json"
    if candidate.exists():
        try:
            with candidate.open("r", encoding="utf-8") as f:
                data = json.load(f)
                LOGGER.info("Schema externo encontrado em {}", candidate.as_posix())
                return data
        except Exception as e:
            LOGGER.warning(
                "Falha ao carregar schema externo '{}': {}. Usando fallback interno.",
                candidate.as_posix(),
                e,
            )
    return _SCHEMA_V3_FALLBACK


def _get_manifest_path(job_dir: Path) -> Path:
    return job_dir / "manifest.json"


def _assert_job_dir(job_dir: Path) -> None:
    if not job_dir.exists() or not job_dir.is_dir():
        raise FileNotFoundError(f"Diretório do job não encontrado: {job_dir}")


def _detect_upload_in_progress(file_path: Path) -> bool:
    # Heurística simples: se nome termina com .part, ainda está em upload
    return file_path.suffix.lower() == ".part"


def _apply_defaults_and_normalize(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica defaults definidos no schema e normalizações convenientes para o pipeline:
    - subperfil_pf default None (apenas PF).
    - reprocessar default False; reprocess_scope default AUTO_MANIFEST.
    - arquivos[*].opcional default False.
    - normaliza tipos e garante presença de chaves esperadas.
    """
    pf = manifest.get("perfil_validacao")
    if pf == "PF":
        manifest["subperfil_pf"] = manifest.get("subperfil_pf", None)
        if manifest["subperfil_pf"] not in ("PF_Pura", "PF_EI", None):
            # Normaliza qualquer valor inválido para None
            LOGGER.warning(
                "Valor inválido para subperfil_pf='{}' → normalizado para None",
                manifest["subperfil_pf"],
            )
            manifest["subperfil_pf"] = None
    else:
        # Para PJ, assegura subperfil_pf ausente/None
        manifest["subperfil_pf"] = None

    manifest["reprocessar"] = bool(manifest.get("reprocessar", False))
    manifest["reprocess_scope"] = manifest.get("reprocess_scope", "AUTO_MANIFEST")
    if manifest["reprocess_scope"] not in ("PDF", "OPENAI", "FULL", "AUTO_MANIFEST"):
        LOGGER.warning(
            "reprocess_scope inválido='{}' → normalizado para AUTO_MANIFEST",
            manifest["reprocess_scope"],
        )
        manifest["reprocess_scope"] = "AUTO_MANIFEST"

    new_files = []
    for idx, arq in enumerate(manifest.get("arquivos", [])):
        arq = dict(arq)  # cópia defensiva
        arq["opcional"] = bool(arq.get("opcional", False))
        # legibilidade_score fica None quando ausente (útil p/ heurísticas posteriores)
        if "legibilidade_score" not in arq:
            arq["legibilidade_score"] = None
        new_files.append(arq)
    manifest["arquivos"] = new_files

    # Garante presença de dicionários vazios quando não fornecidos
    manifest["contexto"] = manifest.get("contexto", {}) or {}
    manifest["metadados"] = manifest.get("metadados", {}) or {}

    return manifest


def _validate_manifest(manifest: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: e.path)
    if errors:
        msgs = []
        for e in errors:
            loc = "/".join([str(p) for p in e.path]) or "<root>"
            msgs.append(f"{loc}: {e.message}")
        raise ValidationError("Manifest inválido:\n- " + "\n- ".join(msgs))


def _check_files_exist(job_dir: Path, manifest: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Verifica se cada arquivo de 'arquivos' existe no diretório do job.
    Retorna:
    - missing: lista de nomes não encontrados
    - uploading: lista de nomes ainda com .part (upload em andamento)
    """
    missing, uploading = [], []
    for item in manifest.get("arquivos", []):
        nome = item["nome"]
        p = job_dir / nome
        if not p.exists():
            missing.append(nome)
            continue
        if _detect_upload_in_progress(p):
            uploading.append(nome)
    return missing, uploading


def _save_normalized_manifest(job_dir: Path, manifest: Dict[str, Any]) -> Path:
    """Grava uma cópia normalizada para auditoria e para o escopo AUTO_MANIFEST."""
    out = job_dir / "manifest.normalizado.json"
    try:
        with out.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        return out
    except Exception as e:
        LOGGER.warning("Falha ao gravar manifest.normalizado.json: {}", e)
        return out


def load_manifest(job_dir: str | Path, strict_files: bool = True) -> Dict[str, Any]:
    """
    Carrega, valida e normaliza o manifest.json de um job.

    Params:
      job_dir: caminho da pasta do job (ex.: /inbox/YYYY/MM/DD/<job_id> ou /processing/<job_id>)
      strict_files: se True, lança erro quando arquivos do manifest não existem
                    (útil após estágio watcher→processing). Se False, apenas loga aviso.

    Returns:
      Um dicionário com o manifest normalizado (schema v3), pronto para uso no pipeline.

    Raises:
      FileNotFoundError, json.JSONDecodeError, ValidationError, RuntimeError
    """
    # 1) Sanitiza job_dir e garante que existe
    job_dir = Path(job_dir)
    _assert_job_dir(job_dir)

    # 2) Define o caminho do manifest (AGORA manifest_path existe, pode logar)
    manifest_path = _get_manifest_path(job_dir)
    LOGGER.info(f"[MANIFEST] Tentando carregar: {manifest_path} (exists={manifest_path.exists()})")
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json não encontrado em {job_dir}")

    # 3) Carrega JSON bruto
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        LOGGER.exception(f"[MANIFEST] JSON inválido em {manifest_path}: {e}")
        raise

    # 4) Normaliza defaults ANTES da validação (permite None em enums etc.)
    raw = _apply_defaults_and_normalize(raw)

    # 5) Carrega schema (externo se existir, senão fallback interno)
    schema = _load_external_schema_if_exists()

    # 6) Valida contra schema
    try:
        _validate_manifest(raw, schema)
    except ValidationError as e:
        LOGGER.exception(f"[MANIFEST] Estrutura inválida: {e}")
        raise

    # 7) Confere existência dos arquivos listados
    missing, uploading = _check_files_exist(job_dir, raw)
    if uploading:
        LOGGER.warning(f"Arquivos ainda em upload (.part) detectados: {uploading} — aguarde estabilização.")
    if missing:
        msg = f"Arquivos listados no manifest não encontrados: {missing}"
        if strict_files:
            raise RuntimeError(msg)
        else:
            LOGGER.warning(msg)

    # 8) Salva cópia normalizada para auditoria / AUTO_MANIFEST
    out_norm = _save_normalized_manifest(job_dir, raw)
    LOGGER.info(f"Manifest carregado e normalizado para job_dir='{job_dir.as_posix()}' → '{out_norm.name}'")

    # 9) Agora sim: podemos logar as chaves do manifest carregado
    try:
        LOGGER.debug({"dbg": "manifest_keys_loaded", "keys": list(raw.keys())})
    except Exception:
        # Em caso de algo inesperado na estrutura (não deve ocorrer)
        LOGGER.debug("[MANIFEST] Não foi possível logar as chaves do manifest.")

    return raw

# -----------------------------
# CLI rápido (opcional p/ debug)
# -----------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Valida e normaliza manifest.json (schema v3)")
    parser.add_argument("job_dir", help="Caminho da pasta do job (com manifest.json)")
    parser.add_argument("--no-strict", action="store_true", help="Não falha se arquivos do manifest não existirem")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.job_dir, strict_files=not args.no_strict)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        LOGGER.info("Manifest OK em '{}'", args.job_dir)
    except Exception as e:
        LOGGER.exception("Falha ao processar manifest em '{}': {}", args.job_dir, e)
        raise
