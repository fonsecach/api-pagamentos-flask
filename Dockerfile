FROM python:3.12-slim-bookworm

# Instala curl e certificados necessários para instalar o uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala o uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Define o PATH com o binário do uv
ENV PATH="/root/.local/bin/:$PATH"

# Diretório de trabalho
WORKDIR /app

# Copia arquivos essenciais
COPY pyproject.toml uv.lock ./

# Instala dependências do projeto
RUN uv sync --no-cache

# Copia o restante da aplicação
COPY . .

# Expondo a porta do Flask (Fly.io usa 8080)
EXPOSE 8080

# Comando de inicialização
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
