"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

from npdfhir.router import router as npdfhir_router

urlpatterns = [
    ##
    # NOTE: (@abachman-dsac) on trailing slashes and routes
    #
    # The common django pattern for permitting optional trailing slashes:
    #
    #   re_path('fhir/?', ...)
    #
    # Allows "/fhirdocs/"" to be a vaild URL, which we do not want.
    #
    # Additionally, the use of an empty path string in npdfhir.urls' urlpatterns
    # `path('', ...)` configuration to mount the rest_framework default router
    # means that we cannot use a single path matcher with 'fhir/' to mount the
    # whole npdfhir app and still resolve https://$hostnam/fhir to the
    # rest_framework.DefaultRouter built-in documentation page.
    #
    # By using two path matchers here and pointing the no-trailing-slash path
    # directly at the rest_framework router api-root view, we can get true
    # optional trailing slashes.
    #
    # The risk for flakiness is due to the fact that `/fhir` is handled by the
    # path configuration in this file and `/fhir/` is handled by the path
    # configuration in `npdfhir.urls` at the `path('', ...)` location.
    #
    # See app/tests/test_routing.py for validation tests to ensure that changes
    # inside npdfhir.urls don't break our routing configuration.
    path("fhir/", include("npdfhir.urls")),
    path("fhir", npdfhir_router.get_api_root_view(), name="api-root"),
    path("admin/", admin.site.urls),
    # everything else goes to provider_directory
    path("", include("provider_directory.urls")),
] + debug_toolbar_urls()
