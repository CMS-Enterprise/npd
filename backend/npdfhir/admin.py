from django.contrib import admin
from .models import Feedback


# read only audit log of users feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("npi", "record_name", "record_id", "formatted_issues", "email", "created_at")
    list_filter = ("created_at", "npi", "record_id")
    search_fields = ("npi", "record_name", "email", "record_id")
    readonly_fields = (
        "id",
        "npi",
        "record_name",
        "record_id",
        "formatted_issues",
        "details",
        "email",
        "created_at",
    )

    # removes add/edit/delete buttons
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # making display of issues cleaner on dashboard
    exclude = ("issues",)

    @admin.display(description="Issues")
    def formatted_issues(self, obj):
        return ", ".join(issue.replace("_", " ").title() for issue in obj.issues)
