from rest_framework import serializers
from .models import *

class RiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ['id', 'fullname', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class RideRequestDriverSerializer(serializers.ModelSerializer):
    rider_name = serializers.CharField(source='rider.fullname', read_only=True)
    rider_email = serializers.CharField(source='rider.email', read_only=True)

    class Meta:
        model = RideRequest
        fields = ['id', 'rider_name', 'rider_email', 'pickup', 'dropoff', 'district', 'status', 'created_at']

class RideRequestSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True, default=None)

    class Meta:
        model = RideRequest
        fields = ['id', 'rider', 'pickup', 'dropoff', 'district', 'status', 'driver_name', 'created_at']
        read_only_fields = ['status', 'created_at']

class RideRequestAdminSerializer(serializers.ModelSerializer):
    rider_name = serializers.CharField(source='rider.fullname', read_only=True)
    driver_name = serializers.CharField(source='driver.name', read_only=True, default=None)
    driver_district = serializers.CharField(source='driver.district', read_only=True, default=None)

    class Meta:
        model = RideRequest
        fields = ['id', 'rider_name', 'pickup', 'dropoff', 'district', 'status', 'driver_name', 'driver_district', 'created_at']
