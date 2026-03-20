from rest_framework import viewsets

from .models import ContentItem, Flag, Keyword
from .serializers import ContentItemSerializer, FlagSerializer, KeywordSerializer
from .services.content_service import ContentService
from .services.flagging_service import FlaggingService


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
    service_class = ContentService

    def perform_create(self, serializer):
        serializer.instance = self.service_class().create_content(serializer.validated_data)


class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagSerializer
    service_class = FlaggingService

    def perform_create(self, serializer):
        serializer.instance = self.service_class().create_flag(serializer.validated_data)
