from django.urls import path

from .views import FlagListAPIView, FlagPartialUpdateAPIView, KeywordCreateAPIView, ScanAPIView

urlpatterns = [
    path('keywords/', KeywordCreateAPIView.as_view(), name='keyword-create'),
    path('scan/', ScanAPIView.as_view(), name='scan'),
    path('flags/', FlagListAPIView.as_view(), name='flag-list'),
    path('flags/<int:pk>/', FlagPartialUpdateAPIView.as_view(), name='flag-partial-update'),
]
