# test_ocr_cnh_pdf.py

import os
from pathlib import Path

from pdf2image import convert_from_path
from extrator_cnh_imagem import extrair_texto_cnh  # reaproveitando seu script

import pytesseract

# Se estiver no Windows, ajuste se necessário:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def pdf_para_png(pdf_path: str, nome_png: str = "cnh_teste.png", dpi: int = 300) -> str:
    """
    Converte a primeira página de um PDF em uma imagem PNG
    e salva na mesma pasta do PDF (ou do script).
    Retorna o caminho completo do PNG gerado.
    """
    pdf_path = Path(pdf_path).resolve()
    diretorio = pdf_path.parent

    pages = convert_from_path(str(pdf_path), dpi=dpi)
    if not pages:
        raise ValueError("PDF sem páginas ou erro na conversão.")

    png_path = diretorio / nome_png
    pages[0].save(str(png_path), "PNG")

    return str(png_path)


def main():
    # Ajuste aqui o nome do PDF da CNH
    nome_pdf = "cnh_mateus.pdf"

    diretorio_script = Path(__file__).parent
    caminho_pdf = diretorio_script / nome_pdf

    print(f"Convertendo PDF para PNG: {caminho_pdf} ...")
    caminho_png = pdf_para_png(caminho_pdf, nome_png="cnh_teste.png", dpi=300)
    print(f"PNG gerado em: {caminho_png}")

    print("\nIniciando OCR da imagem gerada...")
    texto = extrair_texto_cnh(caminho_png)

    if texto:
        print("\n" + "=" * 40)
        print("RESULTADO DO TEXTO EXTRAÍDO")
        print("=" * 40 + "\n")
        print(texto)
        print("\n" + "=" * 40)
    else:
        print("Não foi possível extrair texto da imagem.")


if __name__ == "__main__":
    main()
