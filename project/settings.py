from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from loguru import logger
from django_components import ComponentsSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / 'logs'

logger.add(
    LOG_DIR / 'dj5_helpdesk_{time:YYYY-MM-DD}.log',
    rotation='00:00',
    retention='60 days',
    level='DEBUG',
    encoding='utf-8',
    format='{time:YY-MM-DD HH:mm} | {level} | {message}',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'loguru': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['loguru'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ['DEBUG'] == 'True'

ALLOWED_HOSTS = [host for host in os.environ['ALLOWED_HOSTS'].split(',')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'django_components',
]

COMPONENTS = ComponentsSettings(
    dirs=[
        Path(BASE_DIR) / 'core' / 'components' / 'head',
        Path(BASE_DIR) / 'core' / 'components' / 'main',
        Path(BASE_DIR) / 'core' / 'components' / 'common',
    ],
    reload_on_file_change=True,
)

TAILWIND_CLI_SRC_CSS = 'css/styles.css'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django_components.middleware.ComponentDependencyMiddleware',

]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
        'OPTIONS': {
           'loaders':[(
                'django.template.loaders.cached.Loader', [
                    # Default Django loader
                    'django.template.loaders.filesystem.Loader',
                    # Including this is the same as APP_DIRS=True
                    'django.template.loaders.app_directories.Loader',
                    # Components loader
                    'django_components.template_loader.Loader',
                ]
            )],
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # avoid using {% load component_tags %} in each template
            'builtins': [
                'django_components.templatetags.component_tags',
            ]
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

IS_RUNSERVER = any('runserver' in arg for arg in sys.argv)

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost' if IS_RUNSERVER else os.environ['DB_HOST'],
        'PORT': os.environ.get('DB_PORT', '5432'), 
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

LANGUAGE_CODE = os.environ['LANGUAGE_CODE']

TIME_ZONE = os.environ['TIME_ZONE']

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = 'docker/volumes/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = 'docker/volumes/mediafiles' 

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.environ['STATIC_ROOT']
STATIC_ROOT = os.environ.get('STATIC_ROOT', 'configs/volumes/staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', 'configs/volumes/mediafiles')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core', 'static'),]
STATICFILES_FINDERS = [
    # Default finders
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # Django components
    'django_components.finders.ComponentsFileSystemFinder',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/accounts/logout/' 
LOGIN_URL = '/accounts/login/'
