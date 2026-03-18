from altcha import ChallengeOptions, create_challenge, verify_solution
from datetime import datetime, timezone, timedelta
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.cache import cache
import hashlib


class FeedbackFlowThrottle(AnonRateThrottle):
    rate = "10/min"


class AltchaChallengeView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [FeedbackFlowThrottle]

    def get(self, request):
        challenge = create_challenge(
            ChallengeOptions(
                hmac_key=settings.ALTCHA_HMAC_KEY,
                max_number=100_000,
                expires=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
        )
        return Response(challenge.__dict__)


class FeedbackView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [FeedbackFlowThrottle]

    def post(self, request):
        altcha_payload = request.data.get("altcha")

        if not altcha_payload:
            return Response(
                {"error": "CAPTCHA verification is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        verified = verify_solution(
            altcha_payload,
            settings.ALTCHA_HMAC_KEY,
            check_expires=True,
        )

        if not verified:
            return Response(
                {"error": "CAPTCHA verification failed. Please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # replay prevention
        payload_hash = hashlib.sha256(altcha_payload.encode()).hexdigest()
        cache_key = f"altcha_used:{payload_hash}"

        if cache.get(cache_key):
            return Response(
                {"error": "CAPTCHA verification failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.set(cache_key, True, timeout=60 * 10)

        feedback_data = {
            "uuid": request.data.get("uuid"),
            "record_name": request.data.get("recordName"),
            "issues": request.data.get("issues", []),
            "details": request.data.get("details", ""),
            "email": request.data.get("email", ""),
        }

        # print(feedback_data)
        # send this data to email at this point

        return Response(
            {"message": f"Feedback submitted succcessfuly: {feedback_data}"},
            status=status.HTTP_201_CREATED,
        )
