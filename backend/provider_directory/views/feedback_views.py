from altcha import ChallengeOptions, create_challenge, verify_solution
from datetime import datetime, timezone, timedelta
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
import hashlib
import json
from .feedback_serializer import FeedbackSerializer


class FeedbackFlowThrottle(AnonRateThrottle):
    rate = "10/min"


@extend_schema(exclude=True)
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


@extend_schema(exclude=True)
class FeedbackView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [FeedbackFlowThrottle]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid submission", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        altcha_payload = serializer.validated_data

        try:
            verified = verify_solution(
                altcha_payload,
                settings.ALTCHA_HMAC_KEY,
                check_expires=True,
            )
        except Exception:
            return Response(
                {"error": "CAPTCHA verification failed. Please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not verified:
            return Response(
                {"error": "CAPTCHA verification failed. Please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # replay prevention
        payload_hash = hashlib.sha256(
            json.dumps(altcha_payload["altcha"], sort_keys=True).encode()
        ).hexdigest()
        cache_key = f"altcha_used:{payload_hash}"

        if cache.get(cache_key):
            return Response(
                {"error": "CAPTCHA verification failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.set(cache_key, True, timeout=60 * 10)

        feedback_data = {
            "npi": request.data.get("npi"),
            "record_name": request.data.get("recordName"),
            "issues": request.data.get("issues", []),
            "details": request.data.get("details", ""),
            "email": request.data.get("email", ""),
        }

        print("---------------RESPONSE HERE---------------")
        print(feedback_data)
        # send this data to email at this point

        return Response(
            {"message": f"Feedback submitted succcessfuly: {feedback_data}"},
            status=status.HTTP_201_CREATED,
        )
