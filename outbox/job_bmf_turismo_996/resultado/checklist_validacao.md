# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: RESSALVA
- **Motivos-chave**:
  - Nome empresarial e CNPJ estão corretos.
  - Município e UF da sede estão corretos.
  - Administrador/Responsável na QSA está presente.
  - Prova de assinatura/registro na Junta Comercial está presente.
  - Endereço completo e CEP estão corretos, mas falta atualização do CNAE secundário.
- **Próximas ações**: Solicitar atualização do CNAE secundário.

### Checklist
| Item                       | Critério                               | Status     | Evidências                                         | Ação sugerida                      |
|----------------------------|----------------------------------------|------------|---------------------------------------------------|------------------------------------|
| Contrato                   | Nome empresarial                        | APROVADO   | contrato.pdf p.3 "BMF TURISMO LTDA"               | -                                  |
| Contrato                   | Município e UF                         | APROVADO   | contrato.pdf p.3 "SETE LAGOAS, MG"                | -                                  |
| Contrato                   | Administrador/Responsável na QSA      | APROVADO   | contrato.pdf p.3 "FERNANDO DE LIMA VILA NOVA"    | -                                  |
| Contrato                   | Prova de assinatura/registro           | APROVADO   | contrato.pdf p.9 "Certifico o registro sob o n' 10625434" | -                                  |
| Contrato                   | CNAE secundário                        | RESSALVA   | contrato.pdf p.3 "CNAE secundário não atualizado" | Atualizar CNAE secundário          |
| CPF/CNH do representante    | CPF do representante                   | APROVADO   | cpf_cnh.png p.1 "105.214.676-75"                  | -                                  |
| Procuração                  | Procuração válida                      | INSUFICIENTE | -                                                 | Solicitar Procuração válida        |
| Cartão CNPJ                | Cartão CNPJ                           | APROVADO   | cartao_cnpj.pdf p.1 "22.157.088/0001-92"          | -                                  |

### JSON técnico
```json
{
  "empresa": "BMF TURISMO LTDA",
  "tentativa": 1,
  "documentos_recebidos": [
    "cartao_cnpj.pdf",
    "contrato.pdf",
    "cpf_cnh.png",
    "procuracao.pdf"
  ],
  "checklist": {
    "contrato": {
      "tipo": "Contrato Social",
      "criticos": {
        "nome_empresarial": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "BMF TURISMO LTDA"
            }
          ]
        },
        "municipio": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "SETE LAGOAS, MG"
            }
          ]
        },
        "uf": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "SETE LAGOAS, MG"
            }
          ]
        },
        "qsa_administrador": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "FERNANDO DE LIMA VILA NOVA"
            }
          ]
        },
        "assinatura_junta_ou_juridica": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 9,
              "trecho": "Certifico o registro sob o n' 10625434"
            }
          ]
        }
      },
      "nao_criticos": {
        "endereco": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "Rua Guimaraes Rosa, nº 1000, Sala A, bairro Bom Jardim, CEP 35.701-035"
            }
          ]
        },
        "cep": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "CEP 35.701-035"
            }
          ]
        },
        "enquadramento": {
          "status": "RESSALVA",
          "evidencias": [],
          "observacao": "CNAE secundário não atualizado"
        }
      }
    },
    "cpf_representante": {
      "status": "APROVADO",
      "evidencias": [
        {
          "arquivo": "cpf_cnh.png",
          "pag": 1,
          "trecho": "105.214.676-75"
        }
      ],
      "observacao": ""
    },
    "procuracao": {
      "status": "INSUFICIENTE",
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
    "justificativa": "Atualização do CNAE secundário necessária.",
    "acoes_recomendadas": [
      "Atualizar CNAE secundário"
    ]
  }
}
```

### Histórico Fornecedor
```
[LIBERAÇÃO RESSALVA] – Motivos: Atualização do CNAE secundário necessária. Próximas ações: Atualizar CNAE secundário. Evidências: contrato.pdf p.3 "CNAE secundário não atualizado".
```

### Email sugerido
Assunto: Liberação com ressalva – atualização documental  
Corpo:  
```
Prezados,
Realizamos a validação e a liberação foi efetuada com ressalva.
Pendências a enviar:
• Atualização do CNAE secundário
Assim que recebermos, atualizamos o cadastro.
Atenciosamente,
<assinatura>
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.