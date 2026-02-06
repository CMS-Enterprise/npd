from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from flags.models import FlagState


class TestFeatureFlags(TestCase):
    """
    Visiting the index route when no static/index.html asset exists.
    """

    fixtures = ["auth_user.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", password="nothing")

    def setUp(self):
        self.client.force_login(self.user)

    def test_returns_flags_json(self):
        """
        When static/index.html doesn't exist, route redirects
        """
        response = self.client.get(reverse("provider_directory:frontend_settings"))
        self.assertEqual(response.status_code, 200)

        data = response.json()["feature_flags"]

        self.assertIn("ORGANIZATION_LOOKUP", data)
        self.assertIn("ORGANIZATION_LOOKUP_DETAILS", data)

        self.assertEqual(data["ORGANIZATION_LOOKUP"], False)
        self.assertEqual(data["SEARCH_APP"], False)

    def test_permits_flag_with_group_membership(self):
        # arrange
        FlagState.objects.get_or_create(name="SEARCH_APP", condition="in_group", value="Developers")
        group, _created = Group.objects.get_or_create(name="Developers")
        user = User.objects.get(username="testuser")
        user.groups.add(group)

        # act
        response = self.client.get(reverse("provider_directory:frontend_settings"))

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["feature_flags"]["SEARCH_APP"], True)
