from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

admin.site.index_title = "ISI-Project Admin Panel"
admin.site.site_header = "ISI-Project Admin Panel"
admin.site.site_title = "ISI-Project Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rest_framework.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI endpoints:
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API endpoints
    path(
        "api/v1/", include(
            [
                # Auth endpoints
                path(
                    "oauth/", include([
                        # Token and refresh tokens endpoints
                        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                    ]),
                ),
                # Threads API endpoints
                path("", include("threads.urls")),
            ],
        ),
    ),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += list(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    )
