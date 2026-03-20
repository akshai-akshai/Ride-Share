from django.test import TestCase
from rest_framework.test import APIClient
from .models import Rider, Driver, RideRequest


# MODEL TESTS

class RiderModelTest(TestCase):

    def setUp(self):
        self.rider = Rider.objects.create(
            fullname="Test Rider",
            email="rider@test.com",
            password="pass123"
        )

    def test_rider_created(self):
        self.assertEqual(Rider.objects.count(), 1)

    def test_rider_str(self):
        self.assertEqual(str(self.rider), "Test Rider")

    def test_rider_email_unique(self):
        with self.assertRaises(Exception):
            Rider.objects.create(fullname="Duplicate", email="rider@test.com", password="pass")


class DriverModelTest(TestCase):

    def setUp(self):
        self.driver = Driver.objects.create(
            name="Test Driver",
            email="driver@test.com",
            password="pass123",
            phone="9999999999",
            district="Ernakulam",
            license_number="KL-07-1234",
            vehicle_type="Sedan",
            vehicle_number="KL-07-A-1234"
        )

    def test_driver_created(self):
        self.assertEqual(Driver.objects.count(), 1)

    def test_driver_str(self):
        self.assertEqual(str(self.driver), "Test Driver")

    def test_driver_is_available_default(self):
        self.assertTrue(self.driver.is_available)

    def test_driver_email_unique(self):
        with self.assertRaises(Exception):
            Driver.objects.create(
                name="Dup", email="driver@test.com", password="p",
                phone="0", district="X", license_number="X",
                vehicle_type="X", vehicle_number="X"
            )


class RideRequestModelTest(TestCase):

    def setUp(self):
        self.rider = Rider.objects.create(fullname="Rider A", email="a@test.com", password="pass")
        self.driver = Driver.objects.create(
            name="Driver A", email="da@test.com", password="pass",
            phone="9999999999", district="Ernakulam",
            license_number="KL-01", vehicle_type="SUV", vehicle_number="KL-01-A-0001"
        )
        self.ride = RideRequest.objects.create(
            rider=self.rider,
            pickup="MG Road",
            dropoff="Airport",
            district="Ernakulam"
        )

    def test_ride_created(self):
        self.assertEqual(RideRequest.objects.count(), 1)

    def test_ride_default_status(self):
        self.assertEqual(self.ride.status, "pending")

    def test_ride_str(self):
        self.assertIn("Rider A", str(self.ride))

    def test_ride_assign_driver(self):
        self.ride.driver = self.driver
        self.ride.status = "accepted"
        self.ride.save()
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.driver.name, "Driver A")
        self.assertEqual(self.ride.status, "accepted")

    def test_ride_driver_nullable(self):
        self.assertIsNone(self.ride.driver)



# API TESTS


class RiderAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register_rider(self):
        res = self.client.post("/api/rider/register/", {
            "fullname": "John Doe",
            "email": "john@test.com",
            "password": "pass123"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["message"], "Rider registered successfully")

    def test_register_duplicate_email(self):
        Rider.objects.create(fullname="Existing", email="john@test.com", password="pass")
        res = self.client.post("/api/rider/register/", {
            "fullname": "John", "email": "john@test.com", "password": "pass"
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_login_rider(self):
        Rider.objects.create(fullname="Jane", email="jane@test.com", password="pass123")
        res = self.client.post("/api/rider/login/", {
            "email": "jane@test.com", "password": "pass123"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data["data"]["is_admin"])
        self.assertFalse(res.data["data"]["is_driver"])

    def test_login_admin(self):
        res = self.client.post("/api/rider/login/", {
            "email": "admin111@gmail.com", "password": "111"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["data"]["is_admin"])

    def test_login_wrong_password(self):
        Rider.objects.create(fullname="Jane", email="jane@test.com", password="pass123")
        res = self.client.post("/api/rider/login/", {
            "email": "jane@test.com", "password": "wrongpass"
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_request_ride(self):
        rider = Rider.objects.create(fullname="Rider", email="r@test.com", password="pass")
        res = self.client.post("/api/rider/request-ride/", {
            "rider_id": rider.id,
            "pickup": "MG Road",
            "dropoff": "Airport",
            "district": "Ernakulam"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(RideRequest.objects.count(), 1)

    def test_request_ride_blocks_duplicate_active(self):
        rider = Rider.objects.create(fullname="Rider", email="r@test.com", password="pass")
        RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam", status="pending")
        res = self.client.post("/api/rider/request-ride/", {
            "rider_id": rider.id, "pickup": "C", "dropoff": "D", "district": "Ernakulam"
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_my_rides(self):
        rider = Rider.objects.create(fullname="Rider", email="r@test.com", password="pass")
        RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam")
        res = self.client.get(f"/api/rider/my-rides/?rider_id={rider.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class DriverAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.driver = Driver.objects.create(
            name="Driver One", email="d1@test.com", password="pass",
            phone="9999999999", district="Ernakulam",
            license_number="KL-01", vehicle_type="Sedan", vehicle_number="KL-01-A-0001"
        )

    def test_add_driver(self):
        res = self.client.post("/api/driver/add/", {
            "name": "New Driver", "email": "new@test.com", "password": "pass",
            "phone": "8888888888", "district": "Thrissur",
            "license_number": "KL-10", "vehicle_type": "SUV", "vehicle_number": "KL-10-B-0002"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Driver.objects.count(), 2)

    def test_add_driver_duplicate_email(self):
        res = self.client.post("/api/driver/add/", {
            "name": "Dup", "email": "d1@test.com", "password": "pass",
            "phone": "0", "district": "X", "license_number": "X",
            "vehicle_type": "X", "vehicle_number": "X"
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_login_driver(self):
        res = self.client.post("/api/rider/login/", {
            "email": "d1@test.com", "password": "pass"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["data"]["is_driver"])

    def test_matched_rides(self):
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        RideRequest.objects.create(rider=rider, pickup="MG Road", dropoff="Airport", district="Ernakulam")
        res = self.client.get(f"/api/driver/matched-rides/?driver_id={self.driver.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_accept_ride(self):
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        ride = RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam")
        res = self.client.post("/api/driver/accept-ride/", {
            "driver_id": self.driver.id, "ride_id": ride.id
        }, format="json")
        self.assertEqual(res.status_code, 200)
        ride.refresh_from_db()
        self.assertEqual(ride.status, "accepted")
        self.driver.refresh_from_db()
        self.assertFalse(self.driver.is_available)

    def test_accept_ride_unavailable_driver(self):
        self.driver.is_available = False
        self.driver.save()
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        ride = RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam")
        res = self.client.post("/api/driver/accept-ride/", {
            "driver_id": self.driver.id, "ride_id": ride.id
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_update_status_start(self):
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        ride = RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam", status="accepted", driver=self.driver)
        res = self.client.post("/api/driver/update-status/", {
            "driver_id": self.driver.id, "ride_id": ride.id, "status": "ongoing"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        ride.refresh_from_db()
        self.assertEqual(ride.status, "ongoing")

    def test_update_status_complete(self):
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        ride = RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam", status="ongoing", driver=self.driver)
        res = self.client.post("/api/driver/update-status/", {
            "driver_id": self.driver.id, "ride_id": ride.id, "status": "completed"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        ride.refresh_from_db()
        self.assertEqual(ride.status, "completed")
        self.driver.refresh_from_db()
        self.assertTrue(self.driver.is_available)

    def test_update_status_invalid_transition(self):
        rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        ride = RideRequest.objects.create(rider=rider, pickup="A", dropoff="B", district="Ernakulam", status="pending", driver=self.driver)
        res = self.client.post("/api/driver/update-status/", {
            "driver_id": self.driver.id, "ride_id": ride.id, "status": "completed"
        }, format="json")
        self.assertEqual(res.status_code, 400)


class AdminAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.rider = Rider.objects.create(fullname="R", email="r@test.com", password="pass")
        self.driver = Driver.objects.create(
            name="D", email="d@test.com", password="pass",
            phone="9999999999", district="Ernakulam",
            license_number="KL-01", vehicle_type="Sedan", vehicle_number="KL-01-A-0001"
        )
        self.ride = RideRequest.objects.create(
            rider=self.rider, pickup="MG Road", dropoff="Airport", district="Ernakulam"
        )

    def test_all_rides(self):
        res = self.client.get("/api/admin/rides/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_available_drivers_by_district(self):
        res = self.client.get("/api/admin/available-drivers/?district=Ernakulam")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_available_drivers_wrong_district(self):
        res = self.client.get("/api/admin/available-drivers/?district=Thrissur")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_assign_driver(self):
        res = self.client.post("/api/admin/assign-driver/", {
            "ride_id": self.ride.id, "driver_id": self.driver.id
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, "accepted")
        self.assertEqual(self.ride.driver.id, self.driver.id)

    def test_assign_driver_to_non_pending_ride(self):
        self.ride.status = "accepted"
        self.ride.save()
        res = self.client.post("/api/admin/assign-driver/", {
            "ride_id": self.ride.id, "driver_id": self.driver.id
        }, format="json")
        self.assertEqual(res.status_code, 400)
