from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from flags.models import FlagState


class Command(BaseCommand):
    help = "Create a developer@cms.hhs.gov in the Developers group"

    def prepare_feature_flags(self):
        FlagState.objects.get_or_create(name="SEARCH_APP", condition="in_group", value="Developers")
        FlagState.objects.get_or_create(
            name="PRACTITIONER_LOOKUP", condition="in_group", value="Developers"
        )
        FlagState.objects.get_or_create(
            name="PRACTITIONER_LOOKUP_DETAILS", condition="in_group", value="Developers"
        )
        FlagState.objects.get_or_create(
            name="ORGANIZATION_LOOKUP", condition="in_group", value="Developers"
        )
        FlagState.objects.get_or_create(
            name="ORGANIZATION_LOOKUP_DETAILS", condition="in_group", value="Developers"
        )

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="developer@cms.hhs.gov")
        user.set_password("password123")

        group, _ = Group.objects.get_or_create(name="Developers")
        user.groups.add(group)

        user.save()
        group.save()

        self.prepare_feature_flags()

        self.stdout.write("Created developer@cms.hhs.gov account and added to Developer group")
