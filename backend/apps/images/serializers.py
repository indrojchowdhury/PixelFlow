from django.conf import settings
from rest_framework import serializers

from apps.albums.models import Album
from apps.processing.serializers import ProcessedVersionSerializer

from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    versions = ProcessedVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "album",
            "original_name",
            "original_file",
            "original_size",
            "width",
            "height",
            "format",
            "status",
            "error_message",
            "processing_duration",
            "uploaded_at",
            "versions",
        )
        read_only_fields = fields


class ImageUploadSerializer(serializers.Serializer):
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.none())
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=settings.MAX_FILES_PER_UPLOAD,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # Ownership check: only the user's own albums are valid choices
            self.fields["album"].queryset = Album.objects.filter(user=request.user)