from django.db import models


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ContentItem(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    source = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated', 'title']
        indexes = [
            models.Index(fields=['source'], name='content_source_idx'),
            models.Index(fields=['-last_updated'], name='content_updated_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class Flag(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RELEVANT = 'relevant', 'Relevant'
        IRRELEVANT = 'irrelevant', 'Irrelevant'

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='flags')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='flags')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_reviewed_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['keyword', 'content_item'], name='unique_keyword_content_flag'),
        ]
        indexes = [
            models.Index(fields=['status'], name='flag_status_idx'),
            models.Index(fields=['keyword', 'status'], name='flag_keyword_status_idx'),
            models.Index(fields=['content_item', 'status'], name='flag_content_status_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.keyword} -> {self.content_item} ({self.status})'
