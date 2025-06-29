# API de Pagamentos com Flask e PIX

Este é um projeto de uma API de pagamentos desenvolvida com Flask. A API permite a criação de cobranças PIX, gera um QR Code para o pagamento e exibe uma página de status que é atualizada em tempo real via WebSockets quando o pagamento é confirmado.

## Funcionalidades

-   **Criação de Pagamentos**: Endpoint para criar uma nova cobrança PIX, informando o valor.
-   **Geração de QR Code**: Para cada pagamento criado, um QR Code PIX é gerado e salvo.
-   **Página de Pagamento**: Uma página web é disponibilizada para cada pagamento, exibindo o QR Code, o valor e o status.
-   **Confirmação em Tempo Real**: Utiliza Flask-SocketIO para notificar a página de pagamento em tempo real assim que a cobrança é confirmada, sem a necessidade de recarregar a página.
-   **Testes Automatizados**: Suíte de testes utilizando Pytest para garantir a qualidade e o funcionamento do serviço.
-   **CI/CD e Deploy**: Pipeline de Integração e Entrega Contínua configurado com GitHub Actions para automação de testes e deploy na [Fly.io](https://fly.io/).

## Tecnologias Utilizadas

-   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-SocketIO
-   **Banco de Dados**: SQLite (para desenvolvimento)
-   **Testes**: Pytest
-   **Gerenciador de Dependências**: `uv`
-   **CI/CD**: GitHub Actions
-   **Hospedagem**: Fly.io

## Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

-   Python 3.12+
-   Git
- Uv
- Docker (opcional, mas recomendado)

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/api-pagamentos-flask.git
    cd api-pagamentos-flask
    ```

2.  **Instale o `uv` (se ainda não tiver):**
    `uv` é um instalador e resolvedor de pacotes Python extremamente rápido.
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    Siga as instruções para adicionar o `uv` ao seu PATH.

3.  **Crie e ative um ambiente virtual:**
    ```bash
    uv venv
    ```

4.  **Instale as dependências do projeto com `uv`:**
    O comando `uv sync` irá instalar todas as dependências listadas no `requirements.txt` (ou `pyproject.toml`) no seu ambiente virtual.
    ```bash
    uv sync
    ```

5.  **Execute a aplicação Flask:**
    ```bash
    uv run app.py
    ```
    A aplicação estará disponível em `http://127.0.0.1:5000`.

6.  **Para testar:**
    Você pode criar um pagamento enviando uma requisição POST para o endpoint `/payments/pix`.
    ```bash
    # Exemplo com curl
    curl -X POST -H "Content-Type: application/json" -d '{"value": 150.50}' http://127.0.0.1:5000/payments/pix
    ```
    A resposta conterá o ID do pagamento e a URL para a página de pagamento.

## Automação com GitHub Actions (CI/CD)

O projeto utiliza GitHub Actions para automatizar os testes e o deploy. O workflow está definido em `.github/workflows/fly-deploy.yml`.

### Estrutura do Workflow

O workflow é acionado a cada `push` na branch `main` e consiste em dois jobs:

1.  **`test`**:
    -   **Checkout do código**: Baixa a versão mais recente do código do repositório.
    -   **Instalação do `uv`**: Instala o gerenciador de pacotes `uv`.
    -   **Instalação de dependências**: Usa `uv sync` para instalar as dependências do projeto.
    -   **Execução dos testes**: Roda a suíte de testes com `uv run pytest` para validar a aplicação.

2.  **`deploy`**:
    -   **Dependência**: Este job só é executado se o job `test` for concluído com sucesso (`needs: test`).
    -   **Concorrência**: Garante que apenas um deploy ocorra por vez (`concurrency: group: deploy-group`). Se um novo push for feito, o deploy em andamento é cancelado (`cancel-in-progress: true`).
    -   **Checkout do código**: Baixa o código novamente.
    -   **Configuração do `flyctl`**: Instala e configura a CLI da Fly.io.
    -   **Deploy na Fly.io**: Executa o comando `flyctl deploy --remote-only`, que utiliza os builders remotos da Fly.io para construir e implantar a aplicação. A autenticação é feita através de um token de API.

## Deploy na Fly.io

O deploy na plataforma Fly.io é automatizado pelo workflow do GitHub Actions.

### Configuração

1.  **Arquivo `fly.toml`**: Este arquivo (não fornecido no contexto, mas essencial para o deploy) deve conter as configurações da aplicação na Fly.io, como o nome do app, portas, variáveis de ambiente e processos a serem executados.

2.  **Segredos do GitHub**: Para que o workflow possa se autenticar e realizar o deploy, é necessário configurar um segredo no repositório do GitHub:
    -   Vá para `Settings` > `Secrets and variables` > `Actions`.
    -   Clique em `New repository secret`.
    -   Crie um segredo com o nome `FLY_API_TOKEN`.
    -   O valor do token pode ser obtido executando `fly auth token` no seu terminal (após instalar e autenticar o `flyctl`).

Com essa configuração, a cada push para a branch `main`, a aplicação será testada e, se os testes passarem, uma nova versão será implantada automaticamente na Fly.io.