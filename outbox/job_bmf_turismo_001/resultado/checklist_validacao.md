# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: IMPEDITIVO
- **Motivos-chave**:
  - Falta informação sobre o administrador/representante na QSA.
  - Falta prova de assinatura ou registro na Junta/Cartório.
  - Falta CPF do representante legal.
  - Falta procuração válida se o operador não for o representante legal.
- **Próximas ações**:
  - Enviar documento que comprove o administrador/representante na QSA.
  - Enviar prova de assinatura ou registro na Junta/Cartório.
  - Enviar CPF do representante legal.
  - Enviar procuração válida se o operador não for o representante legal.

### Checklist
| Item                     | Critério                                   | Status     | Evidências                                                   | Ação sugerida                                               |
|--------------------------|--------------------------------------------|------------|-------------------------------------------------------------|------------------------------------------------------------|
| Contrato                 | Outro                                      | IMPEDITIVO |                                                             | Enviar documento que comprove o administrador/representante na QSA. |
| CPF do representante      | Obrigatório                                | IMPEDITIVO |                                                             | Enviar CPF do representante legal.                          |
| Procuração               | Válida se operador ≠ representante legal   | IMPEDITIVO |                                                             | Enviar procuração válida se o operador não for o representante legal. |
| Cartão CNPJ              | Comprovante de Inscrição e Situação Cadastral | APROVADO   | cartao_cnpj.pdf p.1 "NOME EMPRESARIAL\n\nBMF TURISMO LTDA" |                                                            |
| Enquadramento            | Não crítico                                | INSUFICIENTE|                                                             | Enviar informação sobre o enquadramento.                   |

### JSON técnico
```json
{
  "empresa": "BMF TURISMO LTDA",
  "tentativa": 1,
  "documentos_recebidos": [
    "cartao_cnpj.pdf"
  ],
  "checklist": {
    "contrato": {
      "tipo": "Outro",
      "criticos": {
        "nome_empresarial": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "NOME EMPRESARIAL\n\nBMF TURISMO LTDA"
            }
          ]
        },
        "municipio": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "MUNICÍPIO\n\nSETE LAGOAS"
            }
          ]
        },
        "uf": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "UF MG"
            }
          ]
        },
        "qsa_administrador": {
          "status": "INSUFICIENTE",
          "evidencias": [],
          "observacao": "Falta informação sobre o administrador/representante na QSA."
        },
        "assinatura_junta_ou_juridica": {
          "status": "INSUFICIENTE",
          "evidencias": [],
          "observacao": "Falta prova de assinatura ou registro na Junta/Cartório."
        }
      },
      "nao_criticos": {
        "endereco": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "LOGRADOURO\n\nR GUIMARAES ROSA\n\nNÚMERO\n\n1000"
            }
          ]
        },
        "cep": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "CEP\n\n35.701-035"
            }
          ]
        },
        "enquadramento": {
          "status": "INSUFICIENTE",
          "evidencias": [],
          "observacao": "Falta informação sobre o enquadramento."
        }
      }
    },
    "cpf_representante": {
      "status": "INSUFICIENTE",
      "evidencias": [],
      "observacao": "Falta CPF do representante legal."
    },
    "procuracao": {
      "status": "INSUFICIENTE",
      "outorgante": "",
      "outorgado": "",
      "validade": "",
      "evidencias": [],
      "observacao": "Falta procuração válida se o operador não for o representante legal."
    },
    "cartao_cnpj": {
      "status": "APROVADO"
    }
  },
  "regras_disparadas": [],
  "reincidencia": {
    "houve": false,
    "politica": "ressalva_2a_tentativa_vira_impeditivo"
  },
  "decisao_final": {
    "status_global": "IMPEDITIVO",
    "justificativa": "Faltam informações críticas sobre o administrador e a assinatura na Junta/Cartório.",
    "acoes_recomendadas": [
      "Enviar documento que comprove o administrador/representante na QSA.",
      "Enviar prova de assinatura ou registro na Junta/Cartório.",
      "Enviar CPF do representante legal.",
      "Enviar procuração válida se o operador não for o representante legal."
    ]
  }
}
``` 

### Histórico Fornecedor
```
[LIBERAÇÃO IMPEDITIVO] – Motivos: Falta informações críticas sobre o administrador e a assinatura na Junta/Cartório. Próximas ações: Enviar documento que comprove o administrador/representante na QSA, enviar prova de assinatura ou registro na Junta/Cartório, enviar CPF do representante legal, enviar procuração válida se o operador não for o representante legal. Evidências: cartao_cnpj.pdf p.1 "NOME EMPRESARIAL\n\nBMF TURISMO LTDA".
```

### Email sugerido
Assunto: Liberação não aprovada – documentação obrigatória ausente  
Corpo:  
```
Prezados,
A validação não pôde ser concluída devido a impeditivo(s):
• Falta informação sobre o administrador/representante na QSA.
• Falta prova de assinatura ou registro na Junta/Cartório.
• Falta CPF do representante legal.
• Falta procuração válida se o operador não for o representante legal.
Encaminhem os documentos listados para prosseguirmos.
Atenciosamente,
<assinatura>
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.