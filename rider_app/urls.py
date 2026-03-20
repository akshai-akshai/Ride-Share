from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rider', views.RiderViewSet, basename='rider')
router.register(r'driver', views.DriverViewSet, basename='driver')
router.register(r'admin', views.AdminViewSet, basename='admin')

urlpatterns = [
    # Template pages
    path('', views.index, name='index'),
    path('register-page/', views.register_page, name='register-page'),
    path('login-page/', views.login_page, name='login-page'),
    path('rider-home/', views.rider_home, name='rider-home'),
    path('admin-home/', views.admin_home, name='admin-home'),
    path('driver-home/', views.driver_home, name='driver-home'),

    # API routes (via router)
    path('api/', include(router.urls)),
]
