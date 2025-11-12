
# test_openai_connection.py
# Verifica se o .env está sendo carregado e se a OPENAI_API_KEY funciona.
# Uso:  python test_openai_connection.py

import os
import sys
import socket
from dotenv import load_dotenv
from loguru import logger

# Dependendo da versão do pacote 'openai', a importação muda.
# Para a SDK nova:
try:
    from openai import OpenAI
    NEW_SDK = True
except Exception:
    NEW_SDK = False
    import openai  # fallback SDK antigo

def mask_key(key: str, keep: int = 6) -> str:
    if not key:
        return ""
    if len(key) <= keep:
        return "*" * len(key)
    return key[:keep] + "*" * (len(key) - keep)

def internet_ok(host: str = "api.openai.com", port: int = 443, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def main() -> int:
    # 1) Carrega .env (na mesma pasta do script que for executar)
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=dotenv_path, override=True)

    # 2) Lê variáveis
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    logger.remove()
    logger.add(sys.stdout, level="INFO", colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")

    logger.info("Arquivo .env: {}", dotenv_path)
    logger.info("OPENAI_API_KEY: {}", mask_key(api_key))
    logger.info("OPENAI_MODEL  : {}", model)

    if not api_key:
        logger.error("❌ ERRO: Variável OPENAI_API_KEY não encontrada no .env ou ambiente.")
        return 2

    if not internet_ok():
        logger.error("❌ Sem conexão com api.openai.com:443. Verifique VPN/Firewall/Proxy.")
        return 3

    try:
        if NEW_SDK:
            client = OpenAI(api_key=api_key)
            # Teste 1: listar modelos (requisição GET barata)
            resp = client.models.list()
            total = len(resp.data) if hasattr(resp, "data") else "desconhecido"
            logger.info("✅ Conexão OK — /models respondeu. Modelos encontrados: {}", total)

            # Teste 2 (opcional): chamada mínima de chat para validar permissão do modelo
            # reduzida ao essencial para minimizar custo.
            try:
                chat = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Diga 'ok'."}],
                    max_tokens=4,
                    temperature=0.0,
                )
                content = chat.choices[0].message.content if chat and chat.choices else ""
                used = getattr(getattr(chat, "usage", None), "total_tokens", "n/d")
                logger.info("✅ Chat test OK — resposta='{}' | tokens={}", content, used)
            except Exception as e:
                logger.warning("⚠️ Chat test falhou para o modelo '{}'. Erro: {}", model, e)

        else:
            # SDK antigo (openai==0.x)
            openai.api_key = api_key
            # Teste 1: listar modelos
            resp = openai.Model.list()
            total = len(resp.get("data", []))
            logger.info("✅ Conexão OK — /models respondeu. Modelos encontrados: {}", total)
            # Teste 2: chamada mínima (Completion v1) — apenas se disponível
            try:
                chat = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": "Diga 'ok'."}],
                    max_tokens=4,
                    temperature=0.0,
                )
                content = chat["choices"][0]["message"]["content"]
                usage = chat.get("usage", {}).get("total_tokens", "n/d")
                logger.info("✅ Chat test OK — resposta='{}' | tokens={}", content, usage)
            except Exception as e:
                logger.warning("⚠️ Chat test falhou para o modelo '{}'. Erro: {}", model, e)

        logger.info("🎯 Diagnóstico concluído.")
        return 0

    except Exception as e:
        # Erros comuns tratados aqui para diagnóstico mais claro
        msg = str(e)
        if "401" in msg or "invalid" in msg.lower():
            logger.error("❌ Falha de autenticação (401). Verifique a OPENAI_API_KEY.")
        elif "429" in msg or "rate" in msg.lower():
            logger.error("❌ Rate limit. Tente novamente mais tarde ou ajuste o plano.")
        elif "proxy" in msg.lower() or "ssl" in msg.lower():
            logger.error("❌ Problema de rede/SSL/Proxy. Verifique as configurações de rede.")
        else:
            logger.error("❌ Erro inesperado: {}", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())
