"""
main.py
---------
Ponto de entrada da aplicação LICITANET + OCR + OPENAI.

Funções principais:
1. Inicializa logs e estrutura de diretórios
2. Executa o watcher (modo contínuo) ou pipeline manual (modo debug)
3. Integra com interface Streamlit (interface_frontend.py)

Fluxo:
    python main.py                → execução contínua (produção)
    python main.py --debug        → execução manual única (modo debug)
"""

import os
import sys
import argparse
from log_service import get_logger, init_folders

# --- SANITY CHECK OPENAI (início do main.py) ---
from env_loader import get_client, get_model  # usa seu env_loader.py

print(">>> PYTHON ATUAL:", sys.executable)


# main.py — dentro de executar_pipeline_manual()
#from pathlib import Path
#import json

#_folders()
#processing_dir = Path(paths["PROCESSING_DIR"]) / job_id
#manifest_path = processing_dir / "manifest.json"


def sanity_openai() -> None:
    """
    Valida rapidamente se a OPENAI_API_KEY está vindo do .env
    e se a autenticação funciona. Loga key mascarada e modelo.
    """
    client = get_client()              # cria o cliente AGORA, com a key do .env
    model = get_model("gpt-4o-mini")   # lê OPENAI_MODEL do .env (ou usa default)
    key = os.getenv("OPENAI_API_KEY", "")
    masked = (key[:6] + "…" + key[-4:]) if key and len(key) > 10 else "N/D"

    # Log amigável no console
    print(f"[SANITY] OPENAI_MODEL={model} | OPENAI_API_KEY={masked} | Fonte=.env override=True")

    # Chamada leve para confirmar autenticação
    try:
        resp = client.models.list()
        total = len(getattr(resp, "data", []))
        print(f"[SANITY] /models OK — modelos visíveis: {total}")
    except Exception as e:
        print(f"[SANITY] ERRO ao listar modelos: {e}")
# --- FIM SANITY CHECK OPENAI ---


# === Adiciona /modules ao sys.path ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_PATH = os.path.join(CURRENT_DIR, "modules")
if MODULES_PATH not in sys.path:
    sys.path.append(MODULES_PATH)

# Importa módulos principais
from watcher import detect_and_move_jobs
from manifest_loader import load_manifest
from ocr_router import executar_ocr
from doc_verifier_agent import validar_documentos_openai
from consulta_serpro import consultar_cnpj
from relatorio import gerar_relatorio_final

LOGGER = get_logger("main")

def executar_pipeline_manual(job_id: str, dirs: dict):

    """
    Permite rodar o pipeline completo para um job específico manualmente.
    Útil em modo debug ou reprocessamento.
    """
    from pathlib import Path
    from log_service import init_folders
    import json

    processing_dir = Path(dirs["PROCESSING_DIR"])
    LOGGER.warning(f"[DEBUG] Conteúdo da pasta processing ({processing_dir}):")
    for p in processing_dir.iterdir():
        LOGGER.warning(f" - {p}")
    
    global DIRS

    DIRS = init_folders()
    processing_dir = Path(dirs["PROCESSING_DIR"]) / job_id

    manifest_path = processing_dir / "manifest.json"

    LOGGER.warning(f"[DEBUG] Verificando caminho do manifest: {manifest_path.resolve()}")
    LOGGER.warning(f"[DEBUG] Existe? {manifest_path.exists()}")


    if not manifest_path.exists():
        LOGGER.error(f"Manifesto não encontrado para o job {job_id}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    LOGGER.bind(job_id=job_id, evento="DEBUG_EXEC").info("Executando pipeline manual para depuração...")

    # === Etapa 1 - OCR ===
    ocr_result = executar_ocr(job_id, manifest_data)
    # === Etapa 2 - IA Validador 1 ===
    ia1_result = validar_documentos_openai(job_id, ocr_result["dados_extraidos"], manifest_data)
    # === Etapa 3 - Consulta SERPRO ===
    serpro_result = consultar_cnpj(manifest_data)
    # === Etapa 4 - IA Validador 2 ===
    ia2_result = validar_documentos_openai(
        job_id,
        {
            "dados_ocr": ocr_result.get("dados_extraidos", ""),
            "dados_serpro": serpro_result.get("dados", {}),   # ← segue com dict vazio se houver erro/limite
            "resultado_ia1": ia1_result.get("resultado", {}),
            "serpro_disponivel": serpro_result.get("serpro_disponivel", False),
            "serpro_status": serpro_result.get("status", "INDEFINIDO")
        },
        manifest_data,
        modo="comparativo"
    )
    # === Etapa 5 - Relatório Final ===
    gerar_relatorio_final(job_id, manifest_data, ocr_result, ia1_result, serpro_result, ia2_result)

    LOGGER.bind(job_id=job_id, evento="DEBUG_EXEC", status="OK").info("Pipeline manual concluído com sucesso.")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="LICITANET + OCR + OPENAI - Motor de Verificação Documental")
    parser.add_argument("--debug", action="store_true", help="Executa em modo debug (job único)")
    parser.add_argument("--job", type=str, default=None, help="ID do job para execução manual")
    args = parser.parse_args()

    # Inicializa diretórios
    paths = init_folders()
    LOGGER.info("Estrutura de diretórios verificada:")
    for k, v in paths.items():
        print(f"  {k}: {v}")

    if args.debug:
        LOGGER.info("Modo DEBUG ativado")
        if args.job:
            executar_pipeline_manual(args.job, paths)
        else:
            LOGGER.warning("Nenhum job_id informado. Exemplo: python main.py --debug --job job_001")
    else:
        LOGGER.info("Modo PRODUÇÃO - monitoramento contínuo iniciado.")
        detect_and_move_jobs(run_once=False)

if __name__ == "__main__":
    main()
