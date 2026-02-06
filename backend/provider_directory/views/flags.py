# Example API view in Django (using DRF)
from django.conf import settings
from flags.state import flag_enabled
from rest_framework.response import Response
from rest_framework.views import APIView

API_FLAGS = settings.FLAGS.keys()


class FeatureFlagsAPIView(APIView):
    def get(self, request):
        # NOTE: (@abachman-dsac) this approach is easy, but if we end up with
        # complex conditions, it may not be cheap.
        return Response(
            {flag_name: flag_enabled(flag_name, request=request) for flag_name in API_FLAGS}
        )
