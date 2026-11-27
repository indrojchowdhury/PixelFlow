from rest_framework import serializers

from .models import ProcessedVersion


class ProcessedVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedVersion
        fields = (
            "id",
            "version_type",
            "file",
            "file_size",
            "format",
            "width",
            "height",
            "created_at",
        )
        read_only_fields = fields