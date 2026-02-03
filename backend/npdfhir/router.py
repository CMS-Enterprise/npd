from rest_framework.routers import DefaultRouter

from . import views


# NOTE: (@abachman-dsac) even though we're using Django's APPEND_SLASH option,
# we want to ensure we are liberal in what we accept, and strict in what we
# generate for API paths.
#
# ACCEPT:
# - /Endpoint
# - /Endpoint/
# - /Endpoint/12345
# - /Endpoint/12345/
#
# PRODUCE:
# - /Endpoint
# - /Endpoint/12345
#
class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"Practitioner", views.FHIRPractitionerViewSet, basename="fhir-practitioner")
router.register(r"Organization", views.FHIROrganizationViewSet, basename="fhir-organization")
router.register(r"Endpoint", views.FHIREndpointViewSet, basename="fhir-endpoint")
router.register(
    r"PractitionerRole", views.FHIRPractitionerRoleViewSet, basename="fhir-practitionerrole"
)
router.register(r"Location", views.FHIRLocationViewSet, basename="fhir-location")
router.register(
    r"OrganizationAffiliation",
    views.FHIROrganizationAffiliationViewSet,
    basename="fhir-organizationaffiliation",
)
