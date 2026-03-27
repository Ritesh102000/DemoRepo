from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    """Sample model — only staff users can create/edit articles."""
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
