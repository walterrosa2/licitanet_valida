# PRD - Plano de Desenvolvimento de Produto
## Versão 1.0.4 - Estabilização e Portabilidade

### 1. Visão Geral
Esta versão foca na resolução de impedimentos técnicos que bloqueavam a execução da aplicação em ambientes Windows com Docker e na correção de bugs de inicialização que causavam falhas prematuras no pipeline de OCR e IA.

### 2. Problemas Resolvidos
*   **Instabilidade de Permissões:** O sistema de arquivos do Windows (especialmente com OneDrive ativo) bloqueava a criação de pastas pelo container Docker.
*   **Erros de Referência:** Funções sendo chamadas antes de definidas no Python (`NameError`).
*   **Conflitos de Ambiente:** Variáveis de ambiente antigas presas na memória do SO interferiam na autenticação da OpenAI, causando erros 401 (Unauthorized) mesmo com chaves corretas no `.env`.

### 3. Requisitos Técnicos Implementados
*   **Mecanismo de Autoteste de Escrita:** Antes de iniciar o pipeline, a aplicação testa fisicamente a escrita em cada diretório de trabalho. Se falhar, o log informa precisamente o motivo.
*   **Hierarquia de Configuração Dinâmica:** Implementação de prioridade onde o Docker-compose manda no ambiente, mas o `.env` serve como o "porto seguro" para desenvolvimento local.
*   **Higiene de Dados:** Limpeza de strings de API Key para remover espaços invisíveis e comentários acidentais no arquivo `.env`.

### 4. Metas de Qualidade
*   **Sucesso de Build:** Imagem Docker deve ser gerada sem erros de cache de pip.
*   **Portabilidade:** Um novo desenvolvedor deve ser capaz de dar `git clone` e `docker-compose up` e ter o ambiente pronto sem intervenção manual em pastas.
*   **Auditabilidade:** Logs detalhados via `Loguru` capturando falhas de permissão e status de conexão com a OpenAI.
