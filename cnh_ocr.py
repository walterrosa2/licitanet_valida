# cnh_ocr.py
# Módulo especializado para OCR de CNH (Carteira Nacional de Habilitação)
# Integração com o projeto Licitanet + OCR + OpenAI

import os
import cv2
import hashlib
import pytesseract
import numpy as np
from pathlib import Path
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image
from typing import Dict, Any, List, Optional
from log_service import get_logger, init_folders, safe_mkdir
import ledger

# Tenta importar pyzbar para QR Code
try:
    from pyzbar.pyzbar import decode as decode_qr
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
except Exception:
    PYZBAR_AVAILABLE = False

LOGGER = get_logger("cnh_ocr")
DIRS = init_folders()

def process_cnh(
    path_pdf: str,
    job_id: str,
    arquivo_id: str,
    manifest: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Processa um arquivo CNH (PDF ou Imagem), extraindo dados via OCR especializado.
    
    Retorna um dicionário compatível com o pipeline principal, incluindo:
    - conteudo_markdown: Texto extraído formatado
    - cnh_json: Dados estruturados (Nome, CPF, Validade, etc.)
    """
    
    start_time = datetime.now()
    
    # 1. Identificação e Hash
    if not os.path.exists(path_pdf):
        msg = f"Arquivo não encontrado: {path_pdf}"
        LOGGER.error(msg)
        return {"error": msg, "status": "ERRO"}

    hash_pdf = _compute_file_hash(path_pdf)
    
    # OBS: O hash_md só existe DEPOIS do processamento. 
    # Para verificação de idempotência estrita (input igual), usaríamos o hash do PDF.
    # Aqui vamos processar e depois verificar se precisamos registrar ou se já existia idêntico.
    # Pela lógica do ledger atual, should_reprocess pede hash_md também (o que implica ter o resultado anterior).
    # Vamos seguir o fluxo de processar primeiro para garantir os dados.
    
    # 2. Conversão para Imagens
    try:
        images = convert_from_path(path_pdf, dpi=300)
    except Exception as e:
        LOGGER.exception(f"Erro ao converter PDF {path_pdf}: {e}")
        return {"error": str(e), "status": "ERRO"}

    evid_dir = Path(DIRS["EVID_OCR_DIR"]) / job_id
    safe_mkdir(evid_dir)
    
    extracted_text_pages = []
    extracted_data_pages = []
    
    for i, img in enumerate(images):
        page_num = i + 1
        LOGGER.info(f"Processando página {page_num} de {path_pdf}")
        
        # Pré-processamento OpenCV
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Salva ROI original para debug
        # cv2.imwrite(str(evid_dir / f"{arquivo_id}_p{page_num}_orig.png"), img_cv)

        # Pipeline de Extração
        ocr_result = _extract_page_content(img_cv)
        
        # Consolida Texto
        page_md = f"### Página {page_num}\n\n{ocr_result['text']}\n"
        if ocr_result.get('mrz'):
            page_md += f"\n**MRZ Detectado:**\n`{ocr_result['mrz']}`\n"
        
        extracted_text_pages.append(page_md)
        extracted_data_pages.append(ocr_result['data'])
        
        # Tenta ler QR Code se disponível
        if PYZBAR_AVAILABLE:
            qr_data = _read_qr_code(img_cv)
            if qr_data:
                page_md += f"\n**QR Code:** {qr_data}\n"
                ocr_result['data']['qr_code'] = qr_data
                
    # 3. Consolidação Final
    full_markdown = "\n---\n".join(extracted_text_pages)
    
    # Unifica dados estruturados (pega o primeiro não vazio ou merge)
    cnh_json = _merge_cnh_data(extracted_data_pages)
    cnh_json["mrz_full"] = [p.get('mrz') for p in extracted_data_pages if p.get('mrz')]
    
    hash_md = hashlib.sha256(full_markdown.encode('utf-8')).hexdigest()
    
    # 4. Registro no Ledger
    # Verifica se precisava reprocessar (apenas para log, já que processamos)
    # should = ledger.should_reprocess(manifest or {}, job_id, arquivo_id, hash_pdf, hash_md)
    
    ledger.register_entry(
        job_id=job_id,
        arquivo_id=arquivo_id,
        etapa="OCR_CNH",
        hash_pdf=hash_pdf,
        hash_md=hash_md,
        status="OK",
        observacao="Processamento CNH Especializado"
    )
    
    # 5. Salvar Evidências
    md_path = evid_dir / f"{arquivo_id}_cnh.md"
    json_path = evid_dir / f"{arquivo_id}_cnh.json"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    # Retorno compatível
    return {
        "job_id": job_id,
        "arquivo_id": arquivo_id,
        "nome": Path(path_pdf).name,
        "tipo_detectado": "CNH",
        "origem_extracao": "cnh_ocr",
        "tempo_processamento_s": (datetime.now() - start_time).total_seconds(),
        "conteudo_markdown": full_markdown,
        "dados_extraidos": full_markdown, # Compatibilidade com outros módulos que buscam essa chave
        "diagnostico": {
            "fallback_ocr": False,
            "observacoes": ["Processado por cnh_ocr"],
            "qualidade_global": 1.0 # Placeholder
        },
        "cnh_json": cnh_json,
        "evidencias": {
            "markdown": str(md_path),
            "json": str(json_path)
        }
    }


def preprocess_image(img_cv: np.ndarray) -> np.ndarray:
    """Pré-processamento básico para melhorar OCR (User Provided)."""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

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

def _extract_page_content(img_cv: np.ndarray) -> Dict[str, Any]:
    """
    Aplica OCR Tesseract usando configurações validadas pelo user script:
    - PSM 3 (auto)
    - Sem pré-processamento agressivo para o texto principal
    """
    # Converter CV2 (BGR) para PIL (RGB) para Tesseract
    img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    
    # 1. OCR Geral (Português) - Configuração Validada: --psm 3
    config_pt = "--psm 3"
    try:
        text_pt = pytesseract.image_to_string(img_pil, lang="por", config=config_pt)
    except Exception as e:
        LOGGER.warning(f"Erro no OCR PSM 3: {e}")
        text_pt = ""

    # 2. OCR MRZ (Zona inferior) - Mantemos lógica dedicada para reforço
    h, w = img_cv.shape[:2]
    roi_mrz_gray = cv2.cvtColor(img_cv[int(h * 0.65): h, 0:w], cv2.COLOR_BGR2GRAY)
    _, bin_mrz = cv2.threshold(roi_mrz_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    config_mrz = "--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<0123456789"
    try:
        text_mrz = pytesseract.image_to_string(bin_mrz, lang="eng", config=config_mrz)
    except Exception:
        text_mrz = ""
    
    # 3. Parseamento
    data = _parse_text_fields(text_pt)
    mrz_lines = _filter_mrz_lines(text_mrz)
    
    # Adicionar linhas MRZ encontradas no texto geral se não estiverem duplicadas
    mrz_gen = _filter_mrz_lines(text_pt)
    for l in mrz_gen:
        if l not in mrz_lines:
            mrz_lines.append(l)
    
    return {
        "text": text_pt,
        "mrz": "\n".join(mrz_lines) if mrz_lines else None,
        "data": data
    }

def _filter_mrz_lines(text: str) -> List[str]:
    """Filtra linhas que parecem MRZ (I<BRA...)"""
    valid_lines = []
    # Remove quebras de linha excessivas e espaços extras
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    for line in lines:
        l = line.upper().replace(' ', '')
        # Heurística: CNH tem geralmente 30 chars por linha
        # Filtra lixo muito curto
        if len(l) < 10:
            continue
            
        if '<' in l:
            # Verifica padrões comuns de MRZ CNH
            if 'BRA' in l or l.startswith('I<') or l.isdigit() or '<' in l:
                valid_lines.append(l)
    return valid_lines

def _parse_text_fields(text: str) -> Dict[str, str]:
    """
    Extrai campos via Regex simples do texto completo.
    """
    import re
    data = {}
    
    # Regex Genéricos para CNH
    # CPF: 123.456.789-00
    cpf_match = re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
    if cpf_match:
        data['cpf'] = cpf_match.group(0)
        
    # Data: DD/MM/AAAA
    dates = re.findall(r'\d{2}/\d{2}/\d{4}', text)
    if dates:
        # Heurística posicional é frágil em texto corrido, 
        # mas geralmente: Nascimento, Validade, 1ª Hab.
        data['datas_encontradas'] = dates
        # Tenta inferir validade (geralmente a data futura ou última)
        # data['data_validade'] = ... (pode ser melhorado com regex de contexto)

    # Categoria (busca por "Cat." ou isolado)
    cat_match = re.search(r'(?:Cat\.|CATEGORIA)\s*([A-E]{1,2})', text, re.IGNORECASE)
    if cat_match:
        data['categoria'] = cat_match.group(1)
        
    return data

def _read_qr_code(img_cv: np.ndarray) -> Optional[str]:
    """Lê QR Code se existir"""
    try:
        decoded = decode_qr(img_cv)
        if decoded:
            return decoded[0].data.decode("utf-8")
    except Exception:
        pass
    return None

def _merge_cnh_data(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Consolida dados de várias páginas"""
    final = {}
    for p in pages_data:
        for k, v in p.items():
            if v and k not in final:
                final[k] = v
            elif k == "datas_encontradas" and v:
                if "datas_encontradas" not in final:
                    final["datas_encontradas"] = []
                final["datas_encontradas"].extend(v)
    return final

def _compute_file_hash(path: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


