from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


admin.site.index_title = "ISI-Project Admin Panel"
admin.site.site_header = "ISI-Project Admin Panel"
admin.site.site_title = "ISI-Project Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rest_framework.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += list(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    )
