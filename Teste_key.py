from env_loader import get_client, get_model
import os

def sanity_openai():
    client = get_client()
    model = get_model()
    masked = os.getenv("OPENAI_API_KEY", "")[:6] + "****"
    print(f"[SANITY] Model={model} | Key={masked} | Fonte=.env (override=True) OK")

# chame sanity_openai() logo no boot da app
