from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    cover_url = models.URLField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="books_created"
    )
    categories = models.ManyToManyField(
        "Category", through="BookCategory", related_name="books"
    )
