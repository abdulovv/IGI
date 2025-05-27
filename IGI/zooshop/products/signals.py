from .models import Category
from django.db.models.signals import post_save
from django.dispatch import receiver
from slugify import slugify


@receiver(post_save, sender=Category)
def category_post_save(sender, instance, created, **kwargs):
    if created:
        instance.slug = slugify(instance.name)
        instance.save()
