from unittest import mock

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse


def mock_not_found(path: str) -> list[str] | str | None:
    return None


def mock_found(path: str) -> list[str] | str | None:
    return "/some/path/to/index.html"


def mock_render(request, template_name: str, ctx: dict | None = None):
    return HttpResponse(content=f"{template_name} test content")


@mock.patch("provider_directory.views.index.find", mock_not_found)
class WithoutStaticIndex(TestCase):
    """
    Visiting the index route when no static/index.html asset exists.
    """

    fixtures = ["auth_user.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="nothing")

    def setUp(self):
        self.client.force_login(self.user)

    def test_index_redirects_to_vite_in_development(self):
        """
        When static/index.html doesn't exist, route redirects
        """
        response = self.client.get(reverse("provider_directory:index"))
        self.assertRedirects(response, "http://localhost:3000/", fetch_redirect_response=False)


@mock.patch("provider_directory.views.index.find", mock_found)
@mock.patch("provider_directory.views.index.render", mock_render)
class WithStaticIndex(TestCase):
    """
    Visiting the index route when static/index.html asset does exist.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="nothing")

    def setUp(self):
        self.client.force_login(self.user)

    def test_index_serves_static_file(self):
        """
        When static/index.html exists, route serves it
        """
        response = self.client.get(reverse("provider_directory:index"))
        self.assertContains(response, "index.html test content")
