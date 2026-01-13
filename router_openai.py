# router_openai.py
# v3 — LICITANET + OCR + OPENAI
# Módulo responsável por envio de dados à API OpenAI e controle de respostas.

import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from openai import OpenAI
from log_service import get_logger, safe_mkdir
from env_loader import get_client, get_model

logger = get_logger(__name__)

# ==========================================================
# Inicialização
# ==========================================================

MAX_RETRIES = int(os.getenv("MAX_RETRIES_OPENAI", "3"))
OUTBOX_DIR = Path(os.getenv("PATH_OUTBOX", "./outbox"))

MODEL_DEFAULT = get_model("gpt-4o-mini")

# ==========================================================
# Funções auxiliares
# ==========================================================


def save_evidence(job_id: str, stage: str, data: Dict[str, Any]) -> Path:
    """
    Salva evidências de entrada e saída em /outbox/<job_id>/<stage>.json
    """
    out_dir = OUTBOX_DIR / job_id
    safe_mkdir(out_dir)
    file_path = out_dir / f"{stage}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Evidência salva: {file_path}")
    return file_path


def build_prompt(manifest: Dict[str, Any], extracted_text: str) -> str:
    """
    Constrói o prompt conforme o perfil (PF ou PJ).
    No futuro, este conteúdo virá do arquivo prompt_modelo.txt.
    """
    perfil = manifest.get("perfil_validacao", "PJ")
    fornecedor_id = manifest.get("fornecedor_id", "desconhecido")

    if perfil == "PF":
        tipo_pf = manifest.get("subperfil_pf", "PF_Pura")
        prompt = (
            f"Você é um especialista em validação documental de pessoa física ({tipo_pf}).\n"
            f"Analise os documentos extraídos do fornecedor {fornecedor_id} e valide sua consistência.\n\n"
            f"Conteúdo extraído:\n{extracted_text}\n\n"
            f"Responda em JSON estruturado com os seguintes campos:\n"
            f"{{'status': 'válido/inválido', 'motivos': [...], 'dados_extraidos': {{...}}}}\n"
        )
    else:
        prompt = (
            f"Você é um especialista em validação documental de pessoa jurídica.\n"
            f"Analise os documentos extraídos do fornecedor {fornecedor_id} e valide CNPJ, razão social, "
            f"e situação cadastral.\n\n"
            f"Conteúdo extraído:\n{extracted_text}\n\n"
            f"Responda em JSON estruturado com os seguintes campos:\n"
            f"{{'status': 'válido/inválido', 'motivos': [...], 'dados_extraidos': {{...}}}}\n"
        )

    return prompt


def call_openai(prompt: str, model: str = MODEL_DEFAULT, retries: int = MAX_RETRIES) -> str:
    """
    Chama a API OpenAI com retries automáticos e logs detalhados.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Enviando prompt ao OpenAI (tentativa {attempt}/{retries})")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Você é um agente especialista em validação documental."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=4000,
            )
            content = response.choices[0].message.content
            used = getattr(getattr(response, "usage", None), "total_tokens", "n/d")
            logger.info(f"Resposta recebida com sucesso (tokens={used})")
            return content
        except Exception as e:
            logger.warning(f"Erro na chamada OpenAI (tentativa {attempt}): {e}")
            if attempt < retries:
                time.sleep(2 * attempt)
            else:
                raise RuntimeError(f"Falha após {retries} tentativas: {e}")


def parse_response_to_json(response_text: str) -> Dict[str, Any]:
    """
    Tenta converter a resposta da OpenAI em JSON.
    """
    try:
        parsed = json.loads(response_text)
        return parsed
    except json.JSONDecodeError:
        logger.warning("Falha ao converter resposta em JSON. Salvando texto bruto.")
        return {"raw_text": response_text, "erro_parse_json": True}


# ==========================================================
# Função principal
# ==========================================================
def process_with_openai(job_id: str, manifest: Dict[str, Any], extracted_text: str) -> Dict[str, Any]:
    """
    Função principal para enviar texto à OpenAI e obter a resposta estruturada.
    - Gera logs e evidências.
    - Salva entrada e saída em /outbox/<job_id>/
    """
    logger.info(f"Iniciando processamento OpenAI para job_id={job_id}")

    # Salva evidência do prompt enviado
    prompt = build_prompt(manifest, extracted_text)
    save_evidence(job_id, "input_openai", {"prompt": prompt, "manifest": manifest})

    # Chamada à API
    response_text = call_openai(prompt)

    # Salva resposta bruta
    save_evidence(job_id, "output_openai_raw", {"response_text": response_text})

    # Tenta converter resposta em JSON
    parsed = parse_response_to_json(response_text)

    # Salva resposta estruturada
    save_evidence(job_id, "output_openai_parsed", parsed)

    logger.info(f"Processamento OpenAI finalizado para job_id={job_id}")
    return parsed


# ==========================================================
# Teste local
# ==========================================================
if __name__ == "__main__":
    # Exemplo mínimo de teste
    job_id = "TESTE123"
    manifest_exemplo = {
        "fornecedor_id": "123456789",
        "perfil_validacao": "PJ",
        "arquivos": [{"id": "1", "nome": "contrato.pdf"}],
    }
    texto_exemplo = "CNPJ: 12.345.678/0001-99\nRazão Social: Exemplo Ltda\nSituação: ATIVA"

    resultado = process_with_openai(job_id, manifest_exemplo, texto_exemplo)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
