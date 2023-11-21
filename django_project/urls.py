from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from accounts.views import not_cleared_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path('not-cleared/', not_cleared_view, name='not_cleared_url'),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
