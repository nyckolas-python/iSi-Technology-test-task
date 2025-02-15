from isi_app.settings import BASE_DIR

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

JAZZMIN_SETTINGS = {
    "site_title": "My Admin Panel",
    "site_header": "My Company Admin",
    "site_brand": "MyBrand",
    "welcome_sign": "Welcome to My Admin Panel",
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://example.com/support", "new_window": True},
    ],
    "show_ui_builder": True,
    # Other options (see documentation: https://django-jazzmin.readthedocs.io/en/latest/)
}