from unittest import mock
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from provider_directory.views.feedback_serializer import FeedbackSerializer
from npdfhir.models import Feedback


VALID_ALTCHA = {
    "algorithm": "SHA-256",
    "challenge": "abc",
    "number": 42,
    "salt": "salt",
    "signature": "sig",
}

VALID_PAYLOAD = {
    "npi": "1234567890",
    "recordName": "Jane Smith",
    "issues": ["incorrect_endpoint"],
    "details": "",
    "email": "test@example.com",
    "altcha": VALID_ALTCHA,
}

MOCK_PATH = "provider_directory.views.feedback_views.verify_solution"


class FeedbackSerializerTest(TestCase):
    def test_valid_payload(self):
        serializer = FeedbackSerializer(data=VALID_PAYLOAD)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_requires_npi(self):
        data = {**VALID_PAYLOAD, "npi": ""}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("npi", serializer.errors)

    def test_requires_at_least_one_issue(self):
        data = {**VALID_PAYLOAD, "issues": []}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("issues", serializer.errors)

    def test_rejects_invalid_issue_value(self):
        data = {**VALID_PAYLOAD, "issues": ["not_a_real_issue"]}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("issues", serializer.errors)

    def test_accepts_multiple_valid_issues(self):
        data = {
            **VALID_PAYLOAD,
            "issues": ["incorrect_organization_affiliation", "missing_information"],
        }
        serializer = FeedbackSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_other_requires_details(self):
        data = {**VALID_PAYLOAD, "issues": ["other"], "details": ""}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("details", serializer.errors)

    def test_other_with_details_is_valid(self):
        data = {**VALID_PAYLOAD, "issues": ["other"], "details": "Something is wrong"}
        serializer = FeedbackSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_details_max_length(self):
        data = {**VALID_PAYLOAD, "details": "x" * 751}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("details", serializer.errors)

    def test_rejects_invalid_email(self):
        data = {**VALID_PAYLOAD, "email": "not-an-email"}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_email_is_optional(self):
        data = {**VALID_PAYLOAD, "email": ""}
        serializer = FeedbackSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_requires_altcha(self):
        data = {k: v for k, v in VALID_PAYLOAD.items() if k != "altcha"}
        serializer = FeedbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("altcha", serializer.errors)


class AltchaChallengeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(ALTCHA_HMAC_KEY="test-secret-key")
    def test_returns_challenge(self):
        response = self.client.get("/api/altcha")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("challenge", response.data)
        self.assertIn("salt", response.data)
        self.assertIn("algorithm", response.data)


class FeedbackViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def tearDown(self):
        cache.clear()

    @mock.patch(MOCK_PATH, return_value=True)
    def test_successful_submission(self, mock_verify):
        response = self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    @mock.patch(MOCK_PATH, return_value=True)
    def test_creates_feedback_record(self, mock_verify):
        self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        self.assertEqual(Feedback.objects.count(), 1)

        record = Feedback.objects.first()
        self.assertEqual(record.npi, "1234567890")
        self.assertEqual(record.record_name, "Jane Smith")
        self.assertEqual(record.issues, ["incorrect_endpoint"])

    def test_rejects_invalid_payload(self):
        response = self.client.post("/api/feedback/", {"npi": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @mock.patch(MOCK_PATH, return_value=False)
    def test_rejects_failed_captcha(self, mock_verify):
        response = self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CAPTCHA", response.data["error"])

    @mock.patch(MOCK_PATH, side_effect=Exception("bad"))
    def test_handles_captcha_exception(self, mock_verify):
        response = self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CAPTCHA", response.data["error"])

    @mock.patch(MOCK_PATH, return_value=True)
    def test_rejects_replayed_captcha(self, mock_verify):
        self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        response = self.client.post("/api/feedback/", VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CAPTCHA", response.data["error"])
