from django.db import models
from django.utils import timezone


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )


    class Meta:
        abstract = True
