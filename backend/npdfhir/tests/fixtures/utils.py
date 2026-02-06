from ...models import FhirNameUse


def _ensure_name_use():
    return FhirNameUse.objects.get_or_create(value="usual")[0]
