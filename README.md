# 🛒 Marketplace - Projeto de Engenharia de Software

Este é um projeto de um **Marketplace Web** desenvolvido com Django, como parte da disciplina de **Engenharia de Software**. O sistema permite a interação entre **compradores**, **vendedores** e **administradores**, simulando um ambiente de e-commerce completo.

## 📚 Tecnologias Utilizadas

- Python 3.11+
- Django 4.x
- HTML/CSS/Bootstrap
- SQLite (banco de dados padrão)
- Docker (opcional)
- GitHub Actions (CI)

## 🔧 Funcionalidades

- Registro e autenticação de usuários
- Diferenciação entre compradores, vendedores e admins
- Cadastro e listagem de produtos
- Carrinho de compras
- Painel do vendedor
- Painel administrativo
- Testes automatizados
- Deploy com Docker

## 📦 Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/marketplace.git
cd marketplace
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Migre o banco e crie o superusuário

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Rode o servidor

```bash
python manage.py runserver
```

Acesse: [http://localhost:8000](http://localhost:8000)

## 🐳 Rodando com Docker (opcional)

### Build da imagem:

```bash
docker build -t alecsandrodev/marketplace_eng_software:latest .
```

### Rodar o container:

```bash
docker run -p 8000:8000 alecsandrodev/marketplace_eng_software:latest
```

## 🧪 Testes Automatizados

Execute os testes com:

```bash
python manage.py test
```

## 🚀 Deploy Contínuo com GitHub Actions

O projeto já inclui um pipeline CI com GitHub Actions que:

- Instala dependências
- Roda migrações
- Executa os testes unitários

Arquivo: `.github/workflows/django.yml`

## 📁 Estrutura do Projeto

```
marketplace/
├── manage.py
├── marketplace/       # Configurações do projeto
├── users/             # App de autenticação e usuários
├── products/          # App de produtos
├── orders/            # App de pedidos/carrinho
├── templates/         # HTMLs do projeto
└── static/            # Arquivos estáticos (css, js)
```

## 👨‍💻 Autor

**Alecsandro Dev**  
Projeto acadêmico para a disciplina de Engenharia de Software  
[GitHub](https://github.com/alecsandrodev)
