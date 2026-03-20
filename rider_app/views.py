from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Rider, Driver, RideRequest
from .serializers import RiderSerializer, DriverSerializer, RideRequestSerializer, RideRequestAdminSerializer, RideRequestDriverSerializer


# --- Template Views ---

def index(request):
    return render(request, 'index.html')

def register_page(request):
    return render(request, 'register.html')

def login_page(request):
    return render(request, 'login.html')

def rider_home(request):
    return render(request, 'rider_home.html')

def admin_home(request):
    return render(request, 'admin_home.html')

def driver_home(request):
    return render(request, 'driver_home.html')


# --- Rider ViewSet ---

class RiderViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = RiderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Rider registered successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = str(request.data.get('email', '')).strip()
        password = str(request.data.get('password', '')).strip()

        # ADMIN LOGIN
        if email == "admin111@gmail.com" and password == "111":
            return Response({
                "message": "Login successful",
                "data": {"fullname": "Admin", "email": email, "is_admin": True, "is_driver": False}
            })

        # DRIVER LOGIN
        try:
            driver = Driver.objects.get(email=email, password=password)
            return Response({
                "message": "Login successful",
                "data": {
                    "id": driver.id,
                    "name": driver.name,
                    "email": driver.email,
                    "phone": driver.phone,
                    "district": driver.district,
                    "vehicle_type": driver.vehicle_type,
                    "vehicle_number": driver.vehicle_number,
                    "is_admin": False,
                    "is_driver": True
                }
            })
        except Driver.DoesNotExist:
            pass

        # RIDER LOGIN
        try:
            rider = Rider.objects.get(email=email, password=password)
            return Response({
                "message": "Login successful",
                "data": {"id": rider.id, "fullname": rider.fullname, "email": rider.email, "is_admin": False, "is_driver": False}
            })
        except Rider.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='request-ride')
    def request_ride(self, request):
        rider_id = request.data.get('rider_id')
        if not rider_id:
            return Response({"error": "rider_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rider = Rider.objects.get(id=rider_id)
        except Rider.DoesNotExist:
            return Response({"error": "Rider not found"}, status=status.HTTP_404_NOT_FOUND)

        # Block new request if one is already active
        active = RideRequest.objects.filter(rider=rider, status__in=['pending', 'accepted', 'ongoing']).first()
        if active:
            return Response({"error": "You already have an active ride request"}, status=status.HTTP_400_BAD_REQUEST)

        data = {'rider': rider.id, 'pickup': request.data.get('pickup'), 'dropoff': request.data.get('dropoff'), 'district': request.data.get('district')}
        serializer = RideRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ride requested successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-rides')
    def my_rides(self, request):
        rider_id = request.query_params.get('rider_id')
        if not rider_id:
            return Response({"error": "rider_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        rides = RideRequest.objects.filter(rider_id=rider_id).order_by('-created_at')
        serializer = RideRequestSerializer(rides, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-name')
    def update_name(self, request):
        rider_id = request.data.get('rider_id')
        fullname = str(request.data.get('fullname', '')).strip()

        if not fullname:
            return Response({"error": "fullname is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rider = Rider.objects.get(id=rider_id)
        except Rider.DoesNotExist:
            return Response({"error": "Rider not found"}, status=status.HTTP_404_NOT_FOUND)

        rider.fullname = fullname
        rider.save()
        return Response({"message": "Name updated successfully", "fullname": rider.fullname})


# --- Driver ViewSet ---

class DriverViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        if Driver.objects.filter(email=request.data.get('email')).exists():
            return Response({"error": "Driver with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Driver added successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='list')
    def list_drivers(self, request):
        drivers = Driver.objects.all()
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='districts')
    def districts(self, request):
        districts = Driver.objects.values_list('district', flat=True).distinct().order_by('district')
        return Response(list(districts))

    @action(detail=False, methods=['get'], url_path='matched-rides')
    def matched_rides(self, request):
        driver_id = request.query_params.get('driver_id')
        if not driver_id:
            return Response({"error": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        # Match pending rides where ride district equals driver's district
        district_lower = driver.district.lower()
        all_pending = RideRequest.objects.filter(status='pending').select_related('rider')
        matched = [r for r in all_pending if r.district.lower() == district_lower]

        serializer = RideRequestDriverSerializer(matched, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='accept-ride')
    def accept_ride(self, request):
        driver_id = request.data.get('driver_id')
        ride_id = request.data.get('ride_id')

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        if not driver.is_available:
            return Response({"error": "You are not available to accept rides"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ride = RideRequest.objects.get(id=ride_id, status='pending')
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found or already taken"}, status=status.HTTP_404_NOT_FOUND)

        ride.driver = driver
        ride.status = 'accepted'
        ride.save()

        driver.is_available = False
        driver.save()

        return Response({"message": "Ride accepted successfully", "ride_id": ride.id, "status": ride.status})

    @action(detail=False, methods=['get'], url_path='my-rides')
    def driver_rides(self, request):
        driver_id = request.query_params.get('driver_id')
        if not driver_id:
            return Response({"error": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        rides = RideRequest.objects.filter(driver_id=driver_id).order_by('-created_at')
        serializer = RideRequestDriverSerializer(rides, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-status')
    def update_status(self, request):
        driver_id = request.data.get('driver_id')
        ride_id   = request.data.get('ride_id')
        new_status = request.data.get('status')

        ALLOWED_TRANSITIONS = {
            'accepted':  ['ongoing', 'cancelled'],
            'ongoing':   ['completed'],
        }

        try:
            ride = RideRequest.objects.get(id=ride_id, driver_id=driver_id)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)

        allowed = ALLOWED_TRANSITIONS.get(ride.status, [])
        if new_status not in allowed:
            return Response(
                {"error": f"Cannot move from '{ride.status}' to '{new_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ride.status = new_status
        ride.save()

        # Free up driver when ride ends
        if new_status in ['completed', 'cancelled']:
            Driver.objects.filter(id=driver_id).update(is_available=True)

        return Response({"message": f"Ride status updated to '{new_status}'", "status": new_status})


# --- Admin ViewSet ---

class AdminViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='rides')
    def all_rides(self, request):
        rides = RideRequest.objects.select_related('rider', 'driver').order_by('-created_at')
        serializer = RideRequestAdminSerializer(rides, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='available-drivers')
    def available_drivers(self, request):
        district = request.query_params.get('district', '').strip()
        if not district:
            return Response({"error": "district is required"}, status=status.HTTP_400_BAD_REQUEST)
        drivers = Driver.objects.filter(is_available=True, district__iexact=district)
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='assign-driver')
    def assign_driver(self, request):
        ride_id   = request.data.get('ride_id')
        driver_id = request.data.get('driver_id')

        try:
            ride = RideRequest.objects.get(id=ride_id)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)

        if ride.status != 'pending':
            return Response({"error": "Only pending rides can be assigned"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(id=driver_id, is_available=True)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found or not available"}, status=status.HTTP_404_NOT_FOUND)

        ride.driver = driver
        ride.status = 'accepted'
        ride.save()

        driver.is_available = False
        driver.save()

        return Response({
            "message": f"Driver {driver.name} assigned successfully",
            "driver": driver.name,
            "district": driver.district,
            "ride_status": ride.status
        })
