"""
doc_verifier_agent.py
----------------------
Agente de validação documental via OpenAI.

Fluxo:
1. Recebe o texto extraído dos documentos
2. Carrega o prompt base (PF ou PJ)
3. Envia o conteúdo à API OpenAI
4. Salva a resposta e logs em evidências
5. Retorna JSON técnico com status, resposta bruta e estruturada

Dependências:
- openai
- log_service
- dotenv
"""

import os
import json
from datetime import datetime
from pathlib import Path
from log_service import get_logger, init_folders, safe_mkdir
from openai import OpenAI
from env_loader import get_client, get_model
# Inicializações
# Inicializações
LOGGER = get_logger("openai_agent")
DIRS = init_folders()

OPENAI_MODEL = get_model("gpt-4o")
PROMPT_PF_PATH = os.getenv("PROMPT_PF_PATH", "./prompts/prompt_pf_2410.md")
PROMPT_PJ_PATH = os.getenv("PROMPT_PJ_PATH", "./prompts/prompt_pj_2410.md")


def validar_documentos_openai(job_id: str, conteudo: str, manifest: dict, modo: str = "padrao") -> dict:
    """
    Realiza a validação documental via OpenAI.
    modo="padrao" → primeira validação
    modo="comparativo" → validação final comparando dados SERPRO + OCR + IA1
    """
    tipo = manifest.get("tipo", "PJ")
    prompt_path = PROMPT_PJ_PATH if tipo == "PJ" else PROMPT_PF_PATH

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_base = f.read()
    except Exception:
        LOGGER.bind(job_id=job_id, evento="PROMPT", status="ERRO").error(f"Prompt não encontrado em {prompt_path}")
        prompt_base = "Valide o documento conforme as regras padrão."

    # Cria pasta de saída
    evid_dir = Path(DIRS["OUTBOX_DIR"]) / job_id / "ia"
    safe_mkdir(evid_dir)

    # Monta o input final
    entrada = {
        "job_id": job_id,
        "tipo": tipo,
        "modo": modo,
        "conteudo": conteudo
    }

    LOGGER.bind(job_id=job_id, etapa="IA", evento="ENVIO").info(f"Enviando análise para OpenAI ({tipo})...")

    try:
        client = get_client()  # <- garante key do .env no momento da chamada
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt_base},
                {"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}
            ],
            temperature=0.4,
            max_tokens=4000
        )

        resposta = completion.choices[0].message.content.strip()

        # Tenta converter resposta para JSON estruturado
        try:
            resposta_json = json.loads(resposta)
        except Exception:
            resposta_json = {"resposta_livre": resposta}

        # Salva evidências
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        evid_entrada = evid_dir / f"{job_id}_entrada_{modo}_{ts}.json"
        evid_saida = evid_dir / f"{job_id}_saida_{modo}_{ts}.json"

        with open(evid_entrada, "w", encoding="utf-8") as f:
            json.dump(entrada, f, ensure_ascii=False, indent=2)

        with open(evid_saida, "w", encoding="utf-8") as f:
            json.dump(resposta_json, f, ensure_ascii=False, indent=2)

        LOGGER.bind(job_id=job_id, etapa="IA", evento="FIM").info(f"Validação IA concluída para {job_id} ({modo})")

        return {
            "status": "OK",
            "job_id": job_id,
            "modo": modo,
            "resultado": resposta_json,
            "resposta_bruta": resposta,
            "data_execucao": datetime.now().isoformat(),
            "arquivos_evidencia": {
                "entrada": str(evid_entrada),
                "saida": str(evid_saida)
            }
        }

    except Exception as e:
        LOGGER.bind(job_id=job_id, etapa="IA", evento="ERRO").exception(f"Erro ao validar via OpenAI: {e}")
        return {
            "status": "ERRO",
            "job_id": job_id,
            "erro": str(e),
            "modo": modo
        }

# Execução isolada para teste rápido
if __name__ == "__main__":
    dummy_manifest = {
        "job_id": "job_teste",
        "tipo": "PJ"
    }
    resultado = validar_documentos_openai("job_teste", "Conteúdo de exemplo para teste.", dummy_manifest)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
