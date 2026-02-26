from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from . import views
from .router import router

urlpatterns = [
    path("docs/schema/", SpectacularJSONAPIView.as_view(), name="schema"),
    re_path("docs/redoc/?", SpectacularRedocView.as_view(url_name="schema"), name="schema-redoc"),
    re_path("docs/?", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-swagger-ui"),
    path("healthCheck", views.health, name="healthCheck"),
    re_path("metadata/?", views.FHIRCapabilityStatementView.as_view(), name="fhir-metadata"),
    # Router URLs
    # everything else is passed to the rest_framework router to manage
    path("", include(router.urls), name="index"),
] + debug_toolbar_urls()
