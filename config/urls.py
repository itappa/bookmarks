from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [  # noqa: RUF005
        path("admin/", admin.site.urls),
        path("accounts/", include("allauth.urls")),
        path("", include("bookmark.urls")),
        path("rss/", include("rssreader.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + debug_toolbar_urls()
)
