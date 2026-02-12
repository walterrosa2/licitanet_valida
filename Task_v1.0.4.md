# Checklist de Tarefas - Versão 1.0.4

## 🛠 Correções de Código
- [x] Corrigir `NameError: name 'safe_mkdir' is not defined` no `log_service.py` (movida definição para o topo).
- [x] Corrigir typos `get_Logger` para `getLogger` no `log_service.py`.
- [x] Corrigir `TypeError` nas chamadas de `registrar_evento` no `watcher.py` (ajuste de argumentos posicionais/nomeados).
- [x] Implementar teste de escrita proativo no `safe_mkdir` para detectar bloqueios de permissão (ex: Windows/OneDrive).

## 🐋 Docker & Ambiente
- [x] Atualizar `Dockerfile` para pré-criar diretórios e aplicar `chmod 777` no build.
- [x] Ajustar `env_loader.py` para priorizar variáveis do `docker-compose` sobre o `.env` (`override=False`).
- [x] Adicionar limpeza automática de chaves (`.strip()` e remoção de comentários `#`) no `env_loader.py`.
- [x] Atualizar `.gitignore` para manter o repositório limpo de logs, dados e artefatos de teste.

## 🚀 Versionamento & Deploy
- [x] Commit das alterações seguindo padrões técnicos.
- [x] Push do código para o GitHub (main branch).
- [x] Build da imagem Docker local `v1.0.4`.
- [x] Push da imagem para o GHCR (em andamento).

## 🧪 Validação
- [x] Teste de conectividade OpenAI com limpeza de variáveis de memória.
- [x] Verificação de logs do Streamlit para detecção de conflitos de porta e permissão.
