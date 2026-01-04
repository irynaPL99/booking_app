from django.db import models


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Updated At",
    )
    is_deleted = models.BooleanField(
        default=False,  verbose_name="is deleted",
    )


    class Meta:
        abstract = True
