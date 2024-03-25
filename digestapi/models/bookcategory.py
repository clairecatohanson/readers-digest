from django.db import models
from digestapi.models import Book
from digestapi.models import Category


class BookCategory(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="book_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="book_categories"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
