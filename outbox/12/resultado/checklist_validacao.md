# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: IMPEDITIVO
- **Motivos-chave**:
  - Nome empresarial não consta no Cartão CNPJ.
  - Município e UF da sede não estão claros no Cartão CNPJ.
  - Não há evidência de assinatura/registro na Junta Comercial.
  - CPF do representante legal não foi apresentado.
- **Próximas ações**:
  - Enviar o Cartão CNPJ atualizado com nome empresarial, município e UF claros.
  - Apresentar o CPF do representante legal.

### Checklist
| Item                       | Critério                          | Status      | Evidências                                           | Ação sugerida                               |
|----------------------------|-----------------------------------|-------------|-----------------------------------------------------|---------------------------------------------|
| Cartão CNPJ                | Nome empresarial                   | IMPEDITIVO  | cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA" | Enviar Cartão CNPJ atualizado               |
| Cartão CNPJ                | Município e UF da sede            | IMPEDITIVO  | cartao_cnpj.pdf p.1 "SETE LAGOAS MG"                | Enviar Cartão CNPJ atualizado               |
| Contrato Social            | Prova de assinatura/registro      | IMPEDITIVO  | ii_alteracao_contratual_bmf_turismo.pdf p.3 "Certifico o registro sob o nº 10625434" | Enviar documento de registro                 |
| CPF/CNH do representante    | CPF do representante legal         | IMPEDITIVO  | insuficiente                                        | Enviar CPF do representante legal           |
| Procuração                 | Procuração válida                  | INSUFICIENTE| Não apresentada                                     | Enviar Procuração válida se aplicável      |

### JSON técnico
```json
{
  "empresa": "BMF TURISMO LTDA",
  "tentativa": 1,
  "documentos_recebidos": [
    "cartao_cnpj.pdf",
    "ii_alteracao_contratual_bmf_turismo.pdf",
    "fernando_de_lima_vila_nova.pdf"
  ],
  "checklist": {
    "contrato": {
      "tipo": "Outro",
      "criticos": {
        "nome_empresarial": {
          "status": "IMPEDITIVO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "NOME EMPRESARIAL BMF TURISMO LTDA"
            }
          ]
        },
        "municipio": {
          "status": "IMPEDITIVO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "SETE LAGOAS MG"
            }
          ]
        },
        "uf": {
          "status": "IMPEDITIVO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "SETE LAGOAS MG"
            }
          ]
        },
        "qsa_administrador": {
          "status": "IMPEDITIVO",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 3,
              "trecho": "FERNANDO DE LIMA VILA NOVA"
            }
          ]
        },
        "assinatura_junta_ou_juridica": {
          "status": "IMPEDITIVO",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 3,
              "trecho": "Certifico o registro sob o nº 10625434"
            }
          ]
        }
      },
      "nao_criticos": {
        "endereco": {
          "status": "INSUFICIENTE",
          "evidencias": []
        },
        "cep": {
          "status": "INSUFICIENTE",
          "evidencias": []
        },
        "enquadramento": {
          "status": "INSUFICIENTE",
          "evidencias": []
        }
      }
    },
    "cpf_representante": {
      "status": "IMPEDITIVO",
      "evidencias": [],
      "observacao": "CPF do representante legal não foi apresentado."
    },
    "procuracao": {
      "status": "INSUFICIENTE",
      "outorgante": "",
      "outorgado": "",
      "validade": "",
      "evidencias": []
    },
    "cartao_cnpj": {
      "status": "IMPEDITIVO"
    }
  },
  "regras_disparadas": [],
  "reincidencia": {
    "houve": false,
    "politica": "ressalva_2a_tentativa_vira_impeditivo"
  },
  "decisao_final": {
    "status_global": "IMPEDITIVO",
    "justificativa": "Nome empresarial, município e UF da sede não claros. CPF do representante legal não apresentado.",
    "acoes_recomendadas": [
      "Enviar Cartão CNPJ atualizado com nome empresarial, município e UF claros.",
      "Apresentar o CPF do representante legal."
    ]
  }
}
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.