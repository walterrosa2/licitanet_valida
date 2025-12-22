# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: RESSALVA
- **Motivos-chave**:
  - Nome empresarial e CNPJ estão corretos.
  - Município e UF da sede estão corretos.
  - Administrador/Responsável na QSA está presente.
  - Prova de assinatura/registro na Junta Comercial está presente.
  - CPF do representante legal está presente, mas a procuração não foi apresentada.
- **Próximas ações**: Enviar procuração válida ou confirmar que o representante legal é o mesmo que o operador.

### Checklist
| Item                     | Critério                                   | Status      | Evidências                                           | Ação sugerida                                   |
|--------------------------|--------------------------------------------|-------------|-----------------------------------------------------|-------------------------------------------------|
| 1. Cartão CNPJ           | Nome empresarial                           | APROVADO    | `cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA"` | -                                               |
| 2. Cartão CNPJ           | Município e UF da sede                    | APROVADO    | `cartao_cnpj.pdf p.1 "MUNICÍPIO SETE LAGOAS, UF MG"` | -                                               |
| 3. Contrato Social       | Administrador/Responsável na QSA          | APROVADO    | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "FERNANDO DE LIMA VILA NOVA"` | -                                               |
| 4. Contrato Social       | Prova de assinatura/registro               | APROVADO    | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "Certifico o registro sob o n' 10625434"` | -                                               |
| 5. CPF do representante   | CPF do representante legal                 | APROVADO    | `fernando_de_lima_vila_nova.pdf p.1 "CPF 105.214.676-75"` | -                                               |
| 6. Procuração             | Procuração válida                          | RESSALVA    | INSUFICIENTE (procuração não apresentada)           | Enviar procuração válida ou confirmar que o representante legal é o mesmo que o operador. |

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
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "NOME EMPRESARIAL BMF TURISMO LTDA"
            }
          ]
        },
        "municipio": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "MUNICÍPIO SETE LAGOAS, UF MG"
            }
          ]
        },
        "uf": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "cartao_cnpj.pdf",
              "pag": 1,
              "trecho": "MUNICÍPIO SETE LAGOAS, UF MG"
            }
          ]
        },
        "qsa_administrador": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 1,
              "trecho": "FERNANDO DE LIMA VILA NOVA"
            }
          ]
        },
        "assinatura_junta_ou_juridica": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 1,
              "trecho": "Certifico o registro sob o n' 10625434"
            }
          ]
        }
      },
      "nao_criticos": {
        "endereco": {
          "status": "APROVADO"
        },
        "cep": {
          "status": "APROVADO"
        },
        "enquadramento": {
          "status": "APROVADO"
        }
      }
    },
    "cpf_representante": {
      "status": "APROVADO",
      "evidencias": [
        {
          "arquivo": "fernando_de_lima_vila_nova.pdf",
          "pag": 1,
          "trecho": "CPF 105.214.676-75"
        }
      ],
      "observacao": ""
    },
    "procuracao": {
      "status": "RESSALVA",
      "outorgante": "",
      "outorgado": "",
      "validade": "",
      "evidencias": []
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
    "status_global": "RESSALVA",
    "justificativa": "Faltando procuração válida.",
    "acoes_recomendadas": [
      "Enviar procuração válida ou confirmar que o representante legal é o mesmo que o operador."
    ]
  }
}
```

### Histórico Fornecedor
```
[LIBERAÇÃO RESSALVA] – Motivos: Faltando procuração válida. Próximas ações: Enviar procuração válida ou confirmar que o representante legal é o mesmo que o operador. Evidências: cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA".
```

### Email sugerido
Assunto: Liberação com ressalva – atualização documental  
Corpo:  
```
Prezados,
Realizamos a validação e a liberação foi efetuada com ressalva.
Pendências a enviar:
• Procuração válida
Assim que recebermos, atualizamos o cadastro.
Atenciosamente,
<assinatura>
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.