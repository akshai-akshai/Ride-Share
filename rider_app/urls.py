from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rider', views.RiderViewSet, basename='rider')
router.register(r'driver', views.DriverViewSet, basename='driver')
router.register(r'admin', views.AdminViewSet, basename='admin')

urlpatterns = [
    path('api/', include(router.urls)),
]
