from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AbstractBaseModel
from .listing import Listing


class Review(AbstractBaseModel):
    """
    Review model for user feedback on listings.
    """

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Listing"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews",
        verbose_name=_("Author"),
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text=_("Rate from 1 (poor) to 5 (excellent) stars."),
    )
    comment = models.TextField(
        _("Comment"),
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "author"],
                name="unique_review_per_listing_author",
            ),
        ]

    def __str__(self):
        return f"{self.author} → {self.listing} ({self.rating}/5)"
