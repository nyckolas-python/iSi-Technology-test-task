from isi_app.settings import BASE_DIR

STATIC_ROOT = str(BASE_DIR / "static")
MEDIA_ROOT = str(BASE_DIR / "media")

STATIC_URL = "/static/"
MEDIA_URL = "/media/"