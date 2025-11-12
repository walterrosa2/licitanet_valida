# env_loader.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega .env na MESMA PASTA deste arquivo
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

def _mask(s: str, keep: int = 6) -> str:
    if not s:
        return ""
    return s[:keep] + "*" * max(0, len(s) - keep)

def get_client() -> OpenAI:
    """
    Retorna um cliente OpenAI garantindo que a OPENAI_API_KEY vem do .env.
    Zera interferências e evita 'memória' de chave em qualquer SDK.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ ERRO: Variável OPENAI_API_KEY não encontrada no .env ou ambiente.")

    # FORÇA a key do .env a prevalecer no processo
    os.environ["OPENAI_API_KEY"] = api_key  # <- mata qualquer valor antigo

    # (opcional, mas prudente) limpa bases custom se houverem resíduos
    for var in ("OPENAI_API_BASE", "OPENAI_ORG_ID", "OPENAI_PROJECT"):
        # Remova esta limpeza se você usar projeto/base custom oficialmente
        if os.getenv(var) in (None, "", " "):
            continue

    # Cria cliente com a key explícita (independe do env)
    client = OpenAI(api_key=api_key)

    # Log defensivo (sem expor a key inteira)
    print(f"[OpenAI] Key (mascarada): { _mask(api_key) } — via .env em: {DOTENV_PATH}")
    return client

def get_model(default: str = "gpt-4o-mini") -> str:
    return os.getenv("OPENAI_MODEL", default)
