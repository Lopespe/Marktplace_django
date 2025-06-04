# Usa uma imagem oficial do Python como base
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependência
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta usada pelo Django
EXPOSE 8000

# Comando padrão ao iniciar o container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]