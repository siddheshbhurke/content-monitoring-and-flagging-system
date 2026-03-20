from django.db import models


class ContentItem(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    source = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


class FlagRecord(models.Model):
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='flags')
    status = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.content_item_id}:{self.status}'
