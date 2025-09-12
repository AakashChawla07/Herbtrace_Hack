from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'species', views.HerbSpeciesViewSet)
router.register(r'collectors', views.CollectorViewSet)
router.register(r'batches', views.BatchViewSet)
router.register(r'processing-events', views.ProcessingEventViewSet)
router.register(r'quality-tests', views.QualityTestViewSet)
router.register(r'verifications', views.ConsumerVerificationViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
