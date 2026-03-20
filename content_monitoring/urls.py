from rest_framework.routers import DefaultRouter

from .views import ContentItemViewSet, FlagViewSet, KeywordViewSet

router = DefaultRouter()
router.register('keywords', KeywordViewSet, basename='keyword')
router.register('content-items', ContentItemViewSet, basename='content-item')
router.register('flags', FlagViewSet, basename='flag')

urlpatterns = router.urls
