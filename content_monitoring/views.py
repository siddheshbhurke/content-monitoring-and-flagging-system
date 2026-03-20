from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flag, Keyword
from .serializers import (
    FlagSerializer,
    FlagUpdateSerializer,
    KeywordSerializer,
    ScanRequestSerializer,
    ScanSummarySerializer,
)
from .services.content_service import ContentService
from .services.flagging_service import FlaggingService
from .services.keyword_service import KeywordService


class ServiceMixin:
    service_class = None

    def get_service(self):
        if self.service_class is None:
            raise ValueError('service_class must be defined')
        return self.service_class()


class KeywordCreateAPIView(ServiceMixin, generics.CreateAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    service_class = KeywordService

    def perform_create(self, serializer):
        serializer.instance = self.get_service().create_keyword(serializer.validated_data)


class ScanAPIView(ServiceMixin, APIView):
    service_class = ContentService

    def post(self, request, *args, **kwargs):
        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summary = self.get_service().scan_dataset(dataset_path=serializer.validated_data.get('dataset_path'))
        response_serializer = ScanSummarySerializer(summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class FlagListAPIView(generics.ListAPIView):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagSerializer


class FlagPartialUpdateAPIView(ServiceMixin, generics.UpdateAPIView):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagUpdateSerializer
    http_method_names = ['patch']
    service_class = FlaggingService

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_flag = self.get_service().update_flag(instance, serializer.validated_data)
        response_serializer = FlagSerializer(updated_flag)
        return Response(response_serializer.data)
