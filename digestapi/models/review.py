from django.db import models
from django.core import validators
from django.contrib.auth.models import User
from digestapi.models import Book
from django.utils import timezone


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[
            validators.MinValueValidator(limit_value=0),
            validators.MaxValueValidator(limit_value=10),
        ]
    )
    comment = models.CharField(max_length=256)
    date = models.DateField(auto_now_add=True)
