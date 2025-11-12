# env_loader.py
# Carrega variáveis de ambiente do arquivo .env e as aplica globalmente.

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

def load_environment(dotenv_path: str | Path = ".env", override: bool = True) -> None:
    """
    Carrega as variáveis do arquivo .env.
    Se override=True, sobrescreve variáveis existentes no ambiente.
    """
    dotenv_path = Path(dotenv_path)
    if not dotenv_path.exists():
        logger.warning(f"Arquivo .env não encontrado em {dotenv_path.resolve()}")
        return

    load_dotenv(dotenv_path, override=override)
    logger.info(f"Variáveis do .env carregadas de {dotenv_path.resolve()}")

    # Log básico das principais variáveis (sem expor chaves sensíveis)
    for key in [
        "APP_ENV",
        "PATH_INBOX",
        "PATH_PROCESSING",
        "PATH_OUTBOX",
        "PATH_DONE",
        "PATH_ERROR",
    ]:
        value = os.getenv(key)
        logger.info(f"{key} = {value}")

def get_env_variable(key: str, default: str | None = None) -> str | None:
    """Obtém variável de ambiente com fallback."""
    return os.getenv(key, default)

if __name__ == "__main__":
    # Execução direta para teste
    load_environment()
    print("OPENAI_API_KEY:", "***" if os.getenv("OPENAI_API_KEY") else "não definida")
