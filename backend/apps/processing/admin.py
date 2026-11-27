from django.contrib import admin

from .models import ProcessedVersion


@admin.register(ProcessedVersion)
class ProcessedVersionAdmin(admin.ModelAdmin):
    list_display = ("image", "version_type", "width", "height", "file_size", "created_at")
    list_filter = ("version_type",)