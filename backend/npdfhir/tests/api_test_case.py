from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from rest_framework.test import APIClient
from rest_framework.test import APITestCase as DrfAPITestCase
from structlog import contextvars

from ..cache import cacheData as cacheData

# I can't explain why, but we need to import cacheData here. I think we can
# remove this once we move to the docker db setup. By using "import thing as
# thing", we silence "imported but unused" and "not accessed" warnings.


class SqlTraceLogger:
    def __init__(self, testcase: DrfAPITestCase):
        if settings.SQL_TRACING:
            contextvars.bind_contextvars(test=testcase.id())
            connection.force_debug_cursor = True

    def teardown(self):
        if settings.SQL_TRACING:
            connection.force_debug_cursor = False


class APITestCase(DrfAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.user.set_password("nothing")
        return super().setUpTestData()

    def setUp(self):
        super().setUp()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.sql_tracer = SqlTraceLogger(self)

    def tearDown(self):
        super().tearDown()

        self.sql_tracer.teardown()
