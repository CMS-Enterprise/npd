from rest_framework import serializers

VALID_ISSUES = [
    "incorrect_practice_locations",
    "incorrect_phone_numbers",
    "incorrect_taxonomy_or_speciality",
    "incorrect_organization_affiliation",
    "incorrect_endpoint",
    "missing_information",
    "other",
]


class FeedbackSerializer(serializers.Serializer):
    npi = serializers.CharField()
    recordName = serializers.CharField(max_length=255, required=False, allow_blank=True)
    issues = serializers.ListField(
        child=serializers.ChoiceField(choices=VALID_ISSUES),
        min_length=1,
        max_length=len(VALID_ISSUES),
    )
    details = serializers.CharField(max_length=500, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    altcha = serializers.JSONField()

    def validate(self, data):
        if "other" in data.get("issues", []) and not data.get("details", "").strip():
            raise serializers.ValidationError(
                {"details": "Details are required when 'Other' is selected"}
            )
        return data
