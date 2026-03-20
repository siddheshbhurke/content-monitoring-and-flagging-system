from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ContentItem, FlagRecord
from .serializers import ContentItemSerializer, FlagRecordSerializer
from .services.content_service import ContentService
from .services.flagging_service import FlaggingService


class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
    service_class = ContentService

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = self.service_class()
        content_item = service.create_content(serializer.validated_data)
        output = self.get_serializer(content_item)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)


class FlagRecordViewSet(viewsets.ModelViewSet):
    queryset = FlagRecord.objects.all()
    serializer_class = FlagRecordSerializer
    service_class = FlaggingService

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = self.service_class()
        flag_record = service.create_flag(serializer.validated_data)
        output = self.get_serializer(flag_record)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)
