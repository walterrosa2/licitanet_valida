# env_loader.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Localização do arquivo .env
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

# Carrega .env apenas como fallback. 
# Se a variável já existir no Sistema/Docker-compose, ela NÃO será alterada pelo .env.
load_dotenv(dotenv_path=DOTENV_PATH, override=False)

def _mask(s: str, keep: int = 6) -> str:
    if not s or len(s) < keep:
        return "***"
    return s[:keep] + "*" * (len(s) - keep)

def get_client() -> OpenAI:
    """
    Retorna um cliente OpenAI respeitando a prioridade:
    1. Variáveis de Sistema/Docker
    2. Arquivo .env (fallback)
    """
    # Pega a chave, remove espaços e garante que ignore qualquer comentário na mesma linha
    raw_key = os.getenv("OPENAI_API_KEY", "")
    api_key = raw_key.split('#')[0].strip()
    
    # Se a chave do sistema vier vazia (devido ao $env:OPENAI_API_KEY=""), 
    # forçamos a leitura direta do .env novamente ou validamos se ela é válida.
    if not api_key or len(api_key) < 10:
        # Tenta re-carregar com override=True se a chave atual for suspeita
        load_dotenv(dotenv_path=DOTENV_PATH, override=True)
        api_key = os.getenv("OPENAI_API_KEY", "").split('#')[0].strip()
    
    if not api_key:
        raise RuntimeError(f"❌ ERRO: OPENAI_API_KEY não encontrada. Verifique seu .env ou Docker-compose em: {DOTENV_PATH}")

    # Cria cliente com a key explícita
    client = OpenAI(api_key=api_key)

    # Log de segurança
    print(f"[OpenAI] Usando chave iniciada em: { _mask(api_key) }")
    return client

def get_model(default: str = "gpt-4o") -> str:
    return os.getenv("OPENAI_MODEL", default)
