
import os
import sys

def preload():
    print("--- Iniciando pre-download de modelos para a imagem Docker ---")

    # 1. Tenta inicializar o Docling para baixar seus artefatos
    try:
        print("Carregando Docling...")
        from docling.document_converter import DocumentConverter
        # A simples instanciacao ja deve disparar downloads de chaves/modelos padroes
        converter = DocumentConverter()
        print("Docling inicializado com sucesso.")
    except Exception as e:
        print(f"AVISO: Falha ao inicializar Docling no build: {e}")

    # 2. Tenta inicializar RapidOCR (onde deu o erro original)
    try:
        print("Carregando RapidOCR...")
        # Tenta importar via onnxruntime que eh o backend comum do Docling
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr = RapidOCR()
            print("RapidOCR inicializado e modelos baixados.")
        except ImportError:
            print("Modulo rapidocr_onnxruntime nao encontrado, tentando import generico...")
    except Exception as e:
        print(f"AVISO: Falha ao inicializar RapidOCR no build: {e}")

    print("--- Pre-download concluido ---")

if __name__ == "__main__":
    preload()
