from django.db import models
from django.utils import timezone


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )


    class Meta:
        abstract = True
