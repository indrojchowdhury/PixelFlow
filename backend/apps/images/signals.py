from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Image


@receiver(post_delete, sender=Image)
def delete_original_file(sender, instance, **kwargs):
    """Remove the file from storage when the database row is deleted."""
    if instance.original_file:
        instance.original_file.delete(save=False)