from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flag, Keyword
from .serializers import (
    FlagSerializer,
    FlagUpdateSerializer,
    KeywordSerializer,
    ScanRequestSerializer,
    ScanResultSerializer,
)
from .services.content_service import ContentService
from .services.flagging_service import FlaggingService
from .services.keyword_service import KeywordService


class KeywordCreateAPIView(generics.CreateAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    service_class = KeywordService

    def perform_create(self, serializer):
        serializer.instance = self.service_class().create_keyword(serializer.validated_data)


class ScanAPIView(APIView):
    service_class = ContentService

    def post(self, request, *args, **kwargs):
        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content_item = self.service_class().create_and_scan_content(serializer.validated_data)
        output = ScanResultSerializer(content_item)
        return Response(output.data, status=status.HTTP_201_CREATED)


class FlagListAPIView(generics.ListAPIView):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagSerializer


class FlagPartialUpdateAPIView(generics.UpdateAPIView):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagUpdateSerializer
    http_method_names = ['patch']
    service_class = FlaggingService

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_flag = self.service_class().update_flag(instance, serializer.validated_data)
        output = FlagSerializer(updated_flag)
        return Response(output.data)
