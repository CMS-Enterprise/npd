from django.contrib.auth import views as contrib_auth_views
from django.urls import path

from .views import authentication, frontend_settings, index

app_name = "provider_directory"
urlpatterns = [
    # we're only going to provide login / logout functionality, for now
    path("accounts/login/", authentication.LoginView.as_view(), name="login"),
    path("accounts/logout/", contrib_auth_views.LogoutView.as_view(), name="logout"),
    # non-FHIR application API endpoints
    path("api/frontend_settings", frontend_settings.frontend_settings, name="frontend_settings"),
    path(r"", index.index, name="index"),
    path(r"<path:path>", index.index, name="index_with_path"),
]
