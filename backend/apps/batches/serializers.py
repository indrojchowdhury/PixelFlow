from rest_framework import serializers

from .models import ProcessingBatch


class BatchSerializer(serializers.ModelSerializer):
    progress = serializers.FloatField(read_only=True)
    download_available = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingBatch
        fields = (
            "id",
            "album",
            "status",
            "total_images",
            "processed_images",
            "failed_images",
            "progress",
            "download_available",
            "expires_at",
            "created_at",
            "completed_at",
        )
        read_only_fields = fields

    def get_download_available(self, obj):
        return bool(obj.zip_file) and not obj.is_expired