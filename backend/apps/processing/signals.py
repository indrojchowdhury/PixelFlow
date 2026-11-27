from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ProcessedVersion


@receiver(post_delete, sender=ProcessedVersion)
def delete_processed_file(sender, instance, **kwargs):
    """Remove the processed file from storage when its row is deleted."""
    if instance.file:
        instance.file.delete(save=False)