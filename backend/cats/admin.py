from django.contrib import admin
from django.utils import timezone

from .models import Cat


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    """
    Admin interface for Cat model with enhanced features.
    """

    list_display = [
        "id",
        "name",
        "breed",
        "age",
        "color",
        "is_neutered",
        "is_adopted",
        "owner_name",
        "created_at",
    ]

    list_filter = [
        "is_neutered",
        "breed",
        "color",
        "adoption_date",
        "created_at",
    ]

    search_fields = [
        "name",
        "breed",
        "color",
        "owner_name",
        "description",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "is_adopted",
        "age_display",
        "weight_display",
        "status_display",
    ]

    fieldsets = [
        ("Basic Information", {"fields": ["name", "breed", "age", "color", "weight"]}),
        ("Medical Information", {"fields": ["is_neutered"]}),
        ("Adoption Information", {"fields": ["owner_name", "adoption_date"]}),
        ("Additional Information", {"fields": ["description"]}),
        (
            "System Information",
            {
                "fields": [
                    "id",
                    "created_at",
                    "is_adopted",
                    "age_display",
                    "weight_display",
                    "status_display",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    ordering = ["id"]

    # Custom actions
    actions = ["mark_as_adopted", "mark_as_available"]

    def mark_as_adopted(self, request, queryset):
        """Mark selected cats as adopted (admin action)."""
        count = 0
        for cat in queryset:
            if not cat.is_adopted:
                cat.owner_name = "Admin Adoption"
                cat.adoption_date = timezone.now().date()
                cat.save()
                count += 1

        self.message_user(request, f"{count} cats marked as adopted.")

    mark_as_adopted.short_description = "Mark selected cats as adopted"

    def mark_as_available(self, request, queryset):
        """Mark selected cats as available for adoption (admin action)."""
        count = 0
        for cat in queryset:
            if cat.is_adopted:
                cat.owner_name = None
                cat.adoption_date = None
                cat.save()
                count += 1

        self.message_user(request, f"{count} cats marked as available for adoption.")

    mark_as_available.short_description = "Mark selected cats as available"
