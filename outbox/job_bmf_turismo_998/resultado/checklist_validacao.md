# Checklist de Validação

- [x] **resposta_livre** → ### Resumo executivo
- **Status Global**: RESSALVA
- **Motivos‑chave**:
  - Nome empresarial e CNPJ estão corretos.
  - Endereço completo e CEP estão presentes, mas não foram verificados em relação ao Cartão CNPJ.
  - CPF do representante legal está presente.
  - Procuração não foi apresentada, mas não é necessária pois o operador é o representante legal.
  - Cartão CNPJ está presente e é válido.
- **Próximas ações**: Solicitar atualização do endereço completo e do CEP, se houver divergências.

### Checklist
| Item                       | Critério                             | Status     | Evidências                                         | Ação sugerida                          |
|----------------------------|--------------------------------------|------------|---------------------------------------------------|----------------------------------------|
| Cartão CNPJ                | Comprovante de Inscrição e Situação  | APROVADO   | `cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA"` | Nenhuma ação necessária                |
| Contrato Social            | Nome empresarial                      | APROVADO   | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "BMF TURISMO LTDA"` | Nenhuma ação necessária                |
| Contrato Social            | Município e UF                       | RESSALVA   | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "Sete Lagoas, MG"` | Atualizar se houver divergências       |
| Contrato Social            | Administrador/Responsável na QSA    | APROVADO   | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "FERNANDO DE LIMA VILA NOVA"` | Nenhuma ação necessária                |
| Contrato Social            | Prova de assinatura/registro         | APROVADO   | `ii_alteracao_contratual_bmf_turismo.pdf p.1 "Certifico o registro sob o n' 10625434"` | Nenhuma ação necessária                |
| CPF/CNH do representante    | CPF do representante legal            | APROVADO   | `fernando_de_lima_vila_nova.pdf p.1 "105.214.676-75"` | Nenhuma ação necessária                |
| Procuração                  | Procuração válida                    | INSUFICIENTE | Não apresentada                                   | Solicitar procuração se necessário    |

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
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 1,
              "trecho": "BMF TURISMO LTDA"
            }
          ]
        },
        "municipio": {
          "status": "RESSALVA",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 1,
              "trecho": "Sete Lagoas, MG"
            }
          ]
        },
        "uf": {
          "status": "RESSALVA",
          "evidencias": [
            {
              "arquivo": "ii_alteracao_contratual_bmf_turismo.pdf",
              "pag": 1,
              "trecho": "Sete Lagoas, MG"
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
          "status": "RESSALVA"
        },
        "cep": {
          "status": "RESSALVA"
        },
        "enquadramento": {
          "status": "INSUFICIENTE"
        }
      }
    },
    "cpf_representante": {
      "status": "APROVADO",
      "evidencias": [
        {
          "arquivo": "fernando_de_lima_vila_nova.pdf",
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
    "justificativa": "Pendências em endereço e CEP.",
    "acoes_recomendadas": [
      "Atualizar endereço completo e CEP se houver divergências."
    ]
  }
}
```

### Histórico Fornecedor
```
[LIBERAÇÃO RESSALVA] – Motivos: Pendências em endereço e CEP. Próximas ações: Atualizar endereço completo e CEP se houver divergências. Evidências: cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA".
```

### Email sugerido
Assunto: Liberação com ressalva – atualização documental  
Corpo:  
```
Prezados,
Realizamos a validação e a liberação foi efetuada com ressalva.
Pendências a enviar:
• Atualizar endereço completo e CEP se houver divergências.
Assim que recebermos, atualizamos o cadastro.
Atenciosamente,
[Seu Nome]
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.