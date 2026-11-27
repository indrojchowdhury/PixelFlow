from rest_framework import serializers

from .models import Album


class AlbumSerializer(serializers.ModelSerializer):
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = (
            "id",
            "name",
            "description",
            "image_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_image_count(self, obj):
        # The images app does not exist yet. Phase 05 will annotate this value.
        return getattr(obj, "image_count", 0)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")

        user = self.context["request"].user
        queryset = Album.objects.filter(user=user, name__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "You already have an album with this name."
            )
        return value