import pytesseract
from PIL import Image
import os
import sys

# --- CONFIGURAÇÃO PARA USUÁRIOS WINDOWS ---
# Se você estiver no Windows, é muito provável que precise descomentar a linha abaixo
# e ajustar o caminho para onde você instalou o Tesseract.
# Se estiver no Linux ou macOS, geralmente não é necessário, pois ele já está no PATH.

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# -------------------------------------------

def extrair_texto_cnh(caminho_imagem):
    """
    Abre uma imagem de CNH e tenta extrair o texto usando Tesseract OCR.
    """
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return None

    try:
        print(f"Carregando imagem: {caminho_imagem}...")
        img = Image.open(caminho_imagem)

        print("Iniciando OCR (Reconhecimento Óptico de Caracteres)...")
        # A MÁGICA ACONTECE AQUI:
        # image_to_string: Converte a imagem em texto.
        # lang='por': Define o idioma para português (essencial para acentos como ã, é, ç).
        # config='--psm 3': O Page Segmentation Mode 3 é geralmente bom para documentos totalmente automáticos.
        texto_extraido = pytesseract.image_to_string(img, lang='por', config='--psm 3')

        return texto_extraido

    except pytesseract.TesseractNotFoundError:
        print("\nERRO CRÍTICO: O Tesseract não foi encontrado no seu sistema.")
        print("Por favor, certifique-se de que instalou o software Tesseract Engine e configurou o caminho corretamente no início do script.")
        if sys.platform == 'win32':
            print("Dica: No Windows, verifique a variável 'tesseract_cmd' no código.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

# Bloco principal de execução
# Mantenha as importações e a função extrair_texto_cnh iguais ao anterior...
# Apenas substitua a parte final do código por isso:

if __name__ == "__main__":
    # 1. Descobre onde este script Python está salvo no computador
    diretorio_do_script = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Define o nome EXATO do arquivo (conforme sua primeira mensagem)
    nome_do_arquivo = "cnh_teste.png" 
    
    # 3. Cria o caminho completo (Ex: C:\Users\Voce\Documents\cnh_teste.png)
    caminho_completo_imagem = os.path.join(diretorio_do_script, nome_do_arquivo)

    print("--- Iniciando Aplicação de Extração ---")
    print(f"Procurando imagem em: {caminho_completo_imagem}")

    # Chama a função com o caminho completo
    texto = extrair_texto_cnh(caminho_completo_imagem)

    if texto:
        print("\n" + "="*40)
        print("RESULTADO DO TEXTO EXTRAÍDO")
        print("="*40 + "\n")
        print(texto)
        print("\n" + "="*40)
    else:
        print("\nARQUIVO NÃO ENCONTRADO!")
        print(f"Certifique-se de que o arquivo '{nome_do_arquivo}' está na mesma pasta que este script.")
        print(f"Pasta atual: {diretorio_do_script}")