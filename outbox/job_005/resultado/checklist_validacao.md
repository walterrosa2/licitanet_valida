# Checklist de Validação

- [x] **resposta_livre** → **Resumo executivo**  
**Status Global**: IMPEDITIVO  
**Motivos‑chave**:  
- Ausência do Contrato Social.  
- CPF do representante legal não foi fornecido.  
- Não há Procuração válida apresentada.  
- Documentação não atende aos requisitos legais.  
- Divergências críticas nos documentos.  
- Necessidade de regularização da documentação.  
**Próximas ações**: Encaminhar o Contrato Social, CPF do representante legal e Procuração válida.

**Checklist em tabela**  
| Item                     | Critério                               | Status    | Evidências                                      | Ação sugerida         |
|--------------------------|----------------------------------------|-----------|-------------------------------------------------|-----------------------|
| Cartão CNPJ              | Comprovante de Inscrição e Situação    | APROVADO  | cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA" | -                     |
| Contrato/Estatuto/Ata   | Contrato Social                        | IMPEDITIVO | -                                               | Enviar contrato social |
| CPF/CNH do representante  | CPF do representante legal             | IMPEDITIVO | -                                               | Enviar CPF/CNH        |
| Procuração               | Procuração válida                      | IMPEDITIVO | -                                               | Enviar procuração     |

**JSON técnico**  
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
          "status": "IMPEDITIVO",
          "evidencias": []
        },
        "municipio": {
          "status": "IMPEDITIVO",
          "evidencias": []
        },
        "uf": {
          "status": "IMPEDITIVO",
          "evidencias": []
        },
        "qsa_administrador": {
          "status": "IMPEDITIVO",
          "evidencias": []
        },
        "assinatura_junta_ou_juridica": {
          "status": "IMPEDITIVO",
          "evidencias": []
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
      "observacao": "CPF do representante legal não foi fornecido."
    },
    "procuracao": {
      "status": "IMPEDITIVO",
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
    "status_global": "IMPEDITIVO",
    "justificativa": "Documentação não atende aos requisitos legais.",
    "acoes_recomendadas": [
      "Enviar contrato social",
      "Enviar CPF/CNH",
      "Enviar procuração"
    ]
  }
}
```

**historico_fornecedor**:  
```
[LIBERAÇÃO IMPEDITIVO] – Motivos: Ausência do Contrato Social, CPF do representante legal não foi fornecido, e não há Procuração válida apresentada. Próximas ações: Encaminhar o Contrato Social, CPF do representante legal e Procuração válida. Evidências: cartao_cnpj.pdf p.1 "NOME EMPRESARIAL BMF TURISMO LTDA".
```

**email_sugerido**:  
Assunto: Liberação não aprovada – documentação obrigatória ausente  
Corpo:  
```
Prezados,
A validação não pôde ser concluída devido a impeditivo(s):
• Ausência do Contrato Social
• CPF do representante legal não foi fornecido
• Não há Procuração válida apresentada
Encaminhem os documentos listados para prosseguirmos.
Atenciosamente,
<assinatura>
```

---
Gerado automaticamente pela aplicação Licitanet + OCR + OpenAI.