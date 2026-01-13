"""
relatorio.py
--------------
Módulo final do pipeline: consolidação e geração de relatórios.

Fluxo:
1. Recebe resultados de OCR, IA1, SERPRO e IA2
2. Gera:
   - resumo_executivo.md
   - checklist_validacao.md
   - historico.txt
   - email_sugerido.md
   - resultado_tecnico.json
3. Salva tudo no /outbox/<job_id>/resultado/
4. Retorna dicionário com paths das evidências
"""

import os
import json
from datetime import datetime
from pathlib import Path
from log_service import get_logger, init_folders, safe_mkdir

LOGGER = get_logger("relatorio")
DIRS = init_folders()

def gerar_relatorio_final(
    job_id: str,
    manifest: dict,
    ocr_result: dict,
    ia1_result: dict,
    serpro_result: dict,
    ia2_result: dict
) -> dict:
    """
    Consolida todas as saídas e gera os arquivos finais do job.
    """
    out_dir = Path(DIRS["OUTBOX_DIR"]) / job_id / "resultado"
    safe_mkdir(out_dir)

    # === 1. Resumo Executivo ===
    resumo_texto = gerar_resumo_executivo(manifest, ocr_result, ia1_result, serpro_result, ia2_result)
    resumo_path = out_dir / "resumo_executivo.md"
    with open(resumo_path, "w", encoding="utf-8") as f:
        f.write(resumo_texto)

    # === 2. Checklist de Validação ===
    checklist_texto = gerar_checklist_validacao(manifest, ia2_result)
    checklist_path = out_dir / "checklist_validacao.md"
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write(checklist_texto)

    # === 3. Histórico do Fornecedor ===
    historico_texto = gerar_historico_fornecedor(ia2_result)
    historico_path = out_dir / "historico.txt"
    with open(historico_path, "w", encoding="utf-8") as f:
        f.write(historico_texto)

    # === 4. Email Sugerido ===
    email_texto = gerar_email_sugerido(ia2_result)
    email_path = out_dir / "email_sugerido.md"
    with open(email_path, "w", encoding="utf-8") as f:
        f.write(email_texto)

    # === 5. Resultado Técnico JSON ===
    resultado_json = {
        "job_id": job_id,
        "manifest": manifest,
        "ocr_result": ocr_result,
        "ia1_result": ia1_result,
        "serpro_result": serpro_result,
        "ia2_result": ia2_result,
        "arquivos_gerados": {
            "resumo_executivo": str(resumo_path),
            "checklist_validacao": str(checklist_path),
            "historico": str(historico_path),
            "email_sugerido": str(email_path),
        },
        "data_geracao": datetime.now().isoformat()
    }

    resultado_path = out_dir / "resultado_tecnico.json"
    with open(resultado_path, "w", encoding="utf-8") as f:
        json.dump(resultado_json, f, ensure_ascii=False, indent=2)

    LOGGER.bind(job_id=job_id, etapa="RELATORIO", evento="FIM").info(
        f"Relatórios finais gerados em {out_dir}"
    )

    return {
        "status": "OK",
        "job_id": job_id,
        "arquivos": {
            "resumo_executivo": str(resumo_path),
            "checklist": str(checklist_path),
            "historico": str(historico_path),
            "email_sugerido": str(email_path),
            "resultado_tecnico": str(resultado_path)
        }
    }

# ======================================================
# Funções auxiliares
# ======================================================

def gerar_resumo_executivo(manifest, ocr_result, ia1_result, serpro_result, ia2_result) -> str:
    """Gera resumo consolidado para leitura humana."""
    tipo = manifest.get("tipo", "PJ")
    cnpj = manifest.get("cnpj", "Não informado")
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    resumo = f"""# Resumo Executivo — Verificação Documental ({tipo})

**Job:** {manifest.get('job_id')}  
**CNPJ:** {cnpj}  
**Data:** {data}

## Resultado Geral
- OCR: {ocr_result.get('status')}
- IA Validação 1: {ia1_result.get('status')}
- Consulta SERPRO: {serpro_result.get('status')}
- IA Validação 2 (Final): {ia2_result.get('status')}

## Observações Gerais
- O pipeline foi executado automaticamente.
- As evidências estão registradas em `/outbox/{manifest.get('job_id')}/`.

---
"""
    return resumo


def gerar_checklist_validacao(manifest, ia2_result) -> str:
    """Gera checklist básico com base na resposta final da IA."""
    resultado_final = ia2_result.get("resultado", {})
    checklist = "# Checklist de Validação\n\n"

    if isinstance(resultado_final, dict):
        for campo, valor in resultado_final.items():
            checklist += f"- [x] **{campo}** → {valor}\n"
    else:
        checklist += "- [ ] Resultado em formato não estruturado.\n"

    checklist += "\n---\nGerado automaticamente pela aplicação Licitanet + OCR + OpenAI."
    return checklist


def gerar_historico_fornecedor(ia2_result) -> str:
    """Gera histórico consolidado do fornecedor."""
    try:
        historico = ia2_result.get("resultado", {}).get("historico_fornecedor")
        if historico:
            return historico
        status = ia2_result.get("status", "DESCONHECIDO")
        return f"[{status}] — Histórico não fornecido pela IA. Registrar manualmente se necessário."
    except Exception as e:
        return f"Erro ao gerar histórico: {e}"


def gerar_email_sugerido(ia2_result) -> str:
    """Gera o corpo do email sugerido pela IA."""
    try:
        email_info = ia2_result.get("resultado", {}).get("email_sugerido", {})
        assunto = email_info.get("assunto", "[Licitanet] — Resultado de análise documental")
        corpo = email_info.get("corpo", "Prezado fornecedor, sua documentação foi analisada e encontra-se sob o status informado no relatório.")
        return f"**Assunto:** {assunto}\n\n{corpo}"
    except Exception as e:
        return f"Erro ao gerar email sugerido: {e}"
