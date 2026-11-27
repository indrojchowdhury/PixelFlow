from django.contrib import admin

from .models import ProcessingBatch


@admin.register(ProcessingBatch)
class ProcessingBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_images", "processed_images", "failed_images", "created_at")
    list_filter = ("status",)