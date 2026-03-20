from rest_framework.routers import DefaultRouter

from .views import ContentItemViewSet, FlagRecordViewSet

router = DefaultRouter()
router.register('content-items', ContentItemViewSet, basename='content-item')
router.register('flags', FlagRecordViewSet, basename='flag-record')

urlpatterns = router.urls
