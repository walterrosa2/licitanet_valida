# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: RESSALVA
- **Motivos-chave**:
  - Nome empresarial e CNPJ estão corretos.
  - Município e UF da sede estão corretos.
  - Administrador/Responsável na QSA está presente.
  - Prova de assinatura/registro na Junta Comercial está presente.
  - Endereço completo e CEP não estão presentes no contrato social.
- **Próximas ações**: Solicitar atualização do contrato social com o endereço completo e CEP.

### Checklist
| Item                       | Critério                          | Status     | Evidências                                          | Ação sugerida                                   |
|----------------------------|-----------------------------------|------------|----------------------------------------------------|------------------------------------------------|
| Contrato                   | Nome empresarial                   | APROVADO   | contrato.pdf p.3 "BMF TURISMO LTDA"                | -                                              |
| Contrato                   | Município e UF da sede            | APROVADO   | contrato.pdf p.3 "Sete Lagoas, MG"                 | -                                              |
| Contrato                   | Administrador/Responsável na QSA  | APROVADO   | contrato.pdf p.5 "FERNANDO DE LIMA VILA NOVA"     | -                                              |
| Contrato                   | Prova de assinatura/registro       | APROVADO   | contrato.pdf p.9 "Certifico o registro sob o n' 10625434" | -                                              |
| Contrato                   | Endereço completo                  | RESSALVA   | contrato.pdf p.3 "R GUIMARAES ROSA, 1000, SALA A" | Atualizar com o endereço completo e CEP       |
| Contrato                   | CEP                                | RESSALVA   | contrato.pdf p.3 "CEP 35.701-035"                  | Atualizar com o endereço completo e CEP       |
| CPF/CNH do representante    | CPF do representante               | APROVADO   | cpf_cnh.png p.1 "105.214.676-75"                   | -                                              |
| Cartão CNPJ                | Status do Cartão CNPJ             | APROVADO   | cartao_cnpj.pdf p.1 "22.157.088/0001-92"           | -                                              |

### JSON técnico
```json
{
  "empresa": "BMF TURISMO LTDA",
  "tentativa": 1,
  "documentos_recebidos": [
    "cartao_cnpj.pdf",
    "contrato.pdf",
    "cpf_cnh.png"
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
              "trecho": "Sete Lagoas, MG"
            }
          ]
        },
        "uf": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 3,
              "trecho": "Sete Lagoas, MG"
            }
          ]
        },
        "qsa_administrador": {
          "status": "APROVADO",
          "evidencias": [
            {
              "arquivo": "contrato.pdf",
              "pag": 5,
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
          "status": "RESSALVA",
          "evidencias": []
        },
        "cep": {
          "status": "RESSALVA",
          "evidencias": []
        },
        "enquadramento": {
          "status": "INSUFICIENTE",
          "evidencias": []
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
    "justificativa": "Endereço completo e CEP não estão presentes no contrato social.",
    "acoes_recomendadas": [
      "Atualizar com o endereço completo e CEP."
    ]
  }
}
```

### Histórico Fornecedor
```
[LIBERAÇÃO RESSALVA] – Motivos: Endereço completo e CEP não estão presentes no contrato social. Próximas ações: Atualizar com o endereço completo e CEP. Evidências: contrato.pdf p.3 "R GUIMARAES ROSA, 1000, SALA A".
```

### Email sugerido
Assunto: Liberação com ressalva – atualização documental  
Corpo:  
```
Prezados,
Realizamos a validação e a liberação foi efetuada com ressalva.
Pendências a enviar:
• Endereço completo
• CEP
Assim que recebermos, atualizamos o cadastro.
Atenciosamente,
<assinatura>
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.