"""
ledger.py
----------
Módulo de controle de idempotência e auditoria de jobs da aplicação
LICITANET + OCR + OPENAI (v3).

Funções:
1. Registrar execuções concluídas (OCR, IA, SERPRO, etc.)
2. Evitar reprocessamento desnecessário de PDFs já processados
3. Manter histórico completo em formato JSONL (append-only)

Estrutura do ledger (logs/ledger.jsonl):
{
  "timestamp": "2025-11-04T10:32:55",
  "job_id": "job_001",
  "arquivo_id": "a1",
  "etapa": "OCR",
  "hash_pdf": "d0f7a...",
  "hash_md": "fa24b...",
  "status": "OK",
  "observacao": "origem_extracao=docling; tipo_detectado=texto; fallback=False"
}
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from log_service import get_logger, safe_mkdir

LOGGER = get_logger("ledger")

LEDGER_PATH = Path("logs/ledger.jsonl")
safe_mkdir(LEDGER_PATH.parent)

# =====================================================
# 🔹 Função principal: registrar execuções
# =====================================================

def register_entry(
    job_id: str,
    arquivo_id: str,
    etapa: str,
    hash_pdf: str,
    hash_md: str,
    status: str = "OK",
    observacao: str = "",
) -> None:
    """
    Registra uma nova entrada no ledger.
    Cada linha é um JSON independente (append-only).
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "job_id": job_id,
        "arquivo_id": arquivo_id,
        "etapa": etapa,
        "hash_pdf": hash_pdf,
        "hash_md": hash_md,
        "status": status,
        "observacao": observacao,
    }

    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        LOGGER.info(f"Ledger atualizado: {job_id}/{arquivo_id} ({etapa}) → {status}")
    except Exception as e:
        LOGGER.warning(f"Falha ao gravar ledger: {e}")


# =====================================================
# 🔹 Função auxiliar: ler histórico
# =====================================================

def _load_ledger() -> list[Dict[str, Any]]:
    """
    Lê todo o conteúdo do ledger.jsonl e retorna como lista de dicts.
    """
    if not LEDGER_PATH.exists():
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


# =====================================================
# 🔹 Função de idempotência: decidir reprocessamento
# =====================================================

def should_reprocess(
    manifest: Dict[str, Any],
    job_id: str,
    arquivo_id: str,
    hash_pdf: str,
    hash_md: str,
) -> bool:
    """
    Define se um PDF deve ser reprocessado com base nas regras:
    - reprocessar=True no manifest → sempre reprocessa
    - reprocess_scope="PDF|FULL" → reprocessa independente do hash
    - reprocess_scope="OPENAI" → não reprocessa OCR
    - AUTO_MANIFEST → reprocessa somente se hash_pdf mudou
    """
    # Regra explícita do manifest
    if manifest.get("reprocessar") is True:
        escopo = manifest.get("reprocess_scope", "AUTO_MANIFEST")
        if escopo in ["PDF", "FULL"]:
            LOGGER.info(f"[{job_id}/{arquivo_id}] Reprocessamento forçado ({escopo})")
            return True
        elif escopo == "OPENAI":
            LOGGER.info(f"[{job_id}/{arquivo_id}] Escopo OPENAI — OCR não será reprocessado.")
            return False
        # AUTO_MANIFEST → avalia hashes
        LOGGER.info(f"[{job_id}/{arquivo_id}] AUTO_MANIFEST ativado — verificando hash_pdf.")

    # Verifica histórico no ledger
    entries = _load_ledger()
    relevant = [e for e in entries if e["job_id"] == job_id and e["arquivo_id"] == arquivo_id and e["etapa"] == "OCR"]
    if not relevant:
        return True  # nunca processado antes

    last_entry = relevant[-1]  # mais recente
    same_hash = last_entry.get("hash_pdf") == hash_pdf and last_entry.get("hash_md") == hash_md

    if same_hash:
        LOGGER.info(f"[{job_id}/{arquivo_id}] Hashes iguais — pular reprocessamento (idempotência).")
        return False
    else:
        LOGGER.info(f"[{job_id}/{arquivo_id}] Hashes diferentes — reprocessamento necessário.")
        return True


# =====================================================
# 🔹 Função de auditoria rápida
# =====================================================

def consultar_ledger(job_id: Optional[str] = None, arquivo_id: Optional[str] = None) -> list[Dict[str, Any]]:
    """
    Consulta o ledger filtrando por job_id e/ou arquivo_id.
    """
    entries = _load_ledger()
    if job_id:
        entries = [e for e in entries if e["job_id"] == job_id]
    if arquivo_id:
        entries = [e for e in entries if e["arquivo_id"] == arquivo_id]
    return entries


# =====================================================
# 🔹 Teste rápido
# =====================================================

if __name__ == "__main__":
    # Simulação básica
    register_entry(
        job_id="job_demo",
        arquivo_id="a1",
        etapa="OCR",
        hash_pdf="abc123",
        hash_md="def456",
        status="OK",
        observacao="Teste de registro"
    )

    print("Histórico filtrado por job_demo:")
    print(json.dumps(consultar_ledger("job_demo"), indent=2, ensure_ascii=False))
