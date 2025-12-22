import sys
import cv2
import pytesseract
import numpy as np
from pdf2image import convert_from_path
from pathlib import Path

# ================================================
# CONFIGURAÇÕES DO TESSERACT
# ================================================
TESS_CONFIG_GERAL = "--oem 1 --psm 4 -c preserve_interword_spaces=1"
TESS_CONFIG_MRZ = "--oem 1 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<0123456789"

# ================================================
# FUNÇÕES AUXILIARES
# ================================================
def preprocess_image(img):
    """Pré-processamento básico para melhorar OCR."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remoção leve de ruído
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Binarização adaptativa
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )

    return thresh


def extract_mrz(img):
    """Tenta localizar e extrair MRZ (faixa inferior da CNH)."""
    h, w = img.shape[:2]

    # MRZ costuma ocupar ~20% inferior do documento
    roi = img[int(h * 0.70): h, 0:w]

    # Binarizar para MRZ
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    mrz_text = pytesseract.image_to_string(bw, config=TESS_CONFIG_MRZ)
    return mrz_text, roi


# ================================================
# OCR PRINCIPAL DA CNH
# ================================================
def extract_cnh_text(pdf_path):
    print(f"\n🔍 Lendo arquivo: {pdf_path}")

    pages = convert_from_path(pdf_path, dpi=300)
    print(f"➡ {len(pages)} página(s) carregada(s)\n")

    final_text = ""
    mrz_result = ""

    for i, page in enumerate(pages):
        print(f"📄 Processando página {i+1}...")

        img = np.array(page)
        processed = preprocess_image(img)

        # OCR geral (dados estruturados)
        text = pytesseract.image_to_string(processed, config=TESS_CONFIG_GERAL)
        final_text += f"\n\n### Página {i+1}\n{text}\n"

        # OCR MRZ
        mrz_text, roi = extract_mrz(img)
        mrz_result += mrz_text

        # Salva ROI MRZ para depuração
        Path("debug").mkdir(exist_ok=True)
        cv2.imwrite(f"debug/mrz_roi_page_{i+1}.png", roi)

    return final_text, mrz_result


# ================================================
# ENTRYPOINT DO SCRIPT
# ================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_ocr_cnh.py <arquivo.pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    texto, mrz = extract_cnh_text(pdf_file)

    print("\n===================================================")
    print("📝 RESULTADO OCR (TEXTO GERAL)")
    print("===================================================")
    print(texto)

    print("\n===================================================")
    print("🔠 MRZ DETECTADA")
    print("===================================================")
    print(mrz if mrz.strip() else "(nenhuma MRZ reconhecida)")

    print("\n🔎 Arquivos de depuração salvos em ./debug/")
