import sys
import os
import json
from pathlib import Path

# Adiciona o diretório do projeto ao path para importar os módulos
sys.path.append(os.path.join(os.getcwd(), "Licitanet_OCR_OpenAI_V2"))
# Ajuste para rodar da raiz do workspace se necessário, mas o cwd deve estar ok
# Se o script for salvo na raiz do workspace ("Licitanet_OCR_OpenAI_V2" está dentro? Não, parece que estou na raiz de "Projeto_Valida" com base no list_dir user info?
# User info diz:
# [URI] -> walerrosa2/licitanet_valida
# c:\Users\walte\OneDrive\Workspace\IA\LICITANET\Projeto_Valida\Licitanet_OCR_OpenAI_V2
# Vou salvar o script DENTRO de Licitanet_OCR_OpenAI_V2 para facilitar imports relativos.

import ocr_router
from log_service import get_logger

# Configura logger básico para stdout
import logging
logging.basicConfig(level=logging.INFO)

# Monkeypatch em localizar_arquivo para aceitar caminhos absolutos
original_localizar = ocr_router.localizar_arquivo

def mock_localizar_arquivo(job_id, nome):
    # Se o nome já for um caminho absoluto existente, retorna ele
    if os.path.exists(nome):
        return nome
    return original_localizar(job_id, nome)

# Aplica o patch
ocr_router.localizar_arquivo = mock_localizar_arquivo

def run_test():
    # Arquivos identificados (adicionando extensão .jpeg conforme list_dir)
    files = [
        r"C:\Users\walte\OneDrive\Workspace\IA\LICITANET\Projeto_Valida\Dados\Teste_1202\done\WhatsApp Image 2026-02-10 at 08.51.38 (1).jpeg",
        r"C:\Users\walte\OneDrive\Workspace\IA\LICITANET\Projeto_Valida\Dados\Teste_1202\done\WhatsApp Image 2026-02-10 at 08.51.38.jpeg"
    ]

    # Validação prévia
    print("Verificando arquivos...")
    valid_files = []
    for f in files:
        if os.path.exists(f):
            print(f"[OK] Encontrado: {f}")
            valid_files.append({"nome": f})
        else:
            print(f"[ERRO] Não encontrado: {f}")

    if not valid_files:
        print("Nenhum arquivo válido para processar.")
        return

    # Cria manifesto fake
    manifest = {
        "arquivos": valid_files
    }
    job_id = "TESTE_MANUAL_001"

    print(f"\nIniciando OCR para job {job_id}...")
    try:
        resultado = ocr_router.executar_ocr(job_id, manifest)
        print("\n--- RESULTADO FINAL ---\n")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        # Verifica se gerou evidências
        evid_dir = resultado.get("evidencias_dir")
        if evid_dir and os.path.exists(evid_dir):
            print(f"\nDiretório de evidências criado: {evid_dir}")
            print("Arquivos gerados:")
            for f in os.listdir(evid_dir):
                print(f" - {f}")
        else:
            print(f"\nAVISO: Diretório de evidências não encontrado em {evid_dir}")

    except Exception as e:
        print(f"\nERRO CRÍTICO NA EXECUÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
