from isi_app.settings import config

SECRET_KEY = config('SECRET_KEY')
ROOT_URLCONF = 'isi_app.urls'

WSGI_APPLICATION = 'isi_app.wsgi.application'
ASGI_APPLICATION = 'isi_app.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
