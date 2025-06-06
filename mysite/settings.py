"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jr4d9r58@+rp#n6apm1_*ob7nw1eod3mf$w4mji*@^fls9sk_2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # Correto para desenvolvimento. Em produção, você adicionará seus domínios aqui.


# Application definition

INSTALLED_APPS = [
    'marketplace', # Seu app principal, ótimo que está aqui!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', 
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls' # Aponta para o urls.py principal do seu projeto

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Se você tivesse uma pasta 'templates' na raiz do projeto, ela seria listada aqui.
        'APP_DIRS': True, # IMPORTANTE: Permite que o Django encontre templates dentro das pastas 'templates' de cada app.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # Configuração padrão do SQLite, ótima para desenvolvimento.
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Correto para Português do Brasil.

TIME_ZONE = 'America/Sao_Paulo' # Padrão. Você pode mudar para 'America/Sao_Paulo' se for relevante para o seu projeto.

USE_I18N = True # Suporte à internacionalização.

USE_TZ = True # Suporte a timezones.


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


# Diretórios adicionais onde o Django procurará por arquivos estáticos.
# A sua configuração atual faz o Django procurar arquivos diretamente dentro de 'marketplace/static/'.
# Por exemplo, se você tem 'marketplace/static/accounts/css/style.css',
# no template você usaria {% static 'accounts/css/style.css' %}. Isso está funcional.


# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Comente esta linha
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage' # Use esta temporariamente

# Caminho onde o comando `collectstatic` juntará todos os arquivos estáticos para deploy.
# Não é usado diretamente pelo servidor de desenvolvimento para servir arquivos.

STATIC_URL = '/static/'
STATICFILES_DIRS = [
  os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configurações de Autenticação (Login/Logout)
LOGIN_URL = 'marketplace:comprador_login' # Correto! Para onde redirecionar se o usuário não estiver logado.
LOGIN_REDIRECT_URL = 'marketplace:pagina_inicial_comprador' # Correto! Para onde ir após login bem-sucedido.
LOGOUT_REDIRECT_URL = 'marketplace:landing_page' # Correto! Para onde ir após logout.


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'teste@gmail.com' # Um email qualquer para o remetente

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')