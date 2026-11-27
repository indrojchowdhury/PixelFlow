from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("original_name", "user", "album", "status", "original_size", "uploaded_at")
    list_filter = ("status", "format")
    search_fields = ("original_name", "user__username")