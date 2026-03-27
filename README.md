🚖 Ride Share — Django REST API

A backend web API for a ride-sharing platform built using Django and Django REST Framework (DRF).
The system supports three types of users: Riders, Drivers, and Admin, with role-specific features and ride lifecycle management.

📌 Features
👤 Rider
Register a new account
Login (shared endpoint for all roles)
Request a ride (restricted if an active ride exists)
View ride history
Update profile (display name)
🚗 Driver
View all drivers and available districts
View matched ride requests (based on district)
Accept rides (automatically marks driver unavailable)
View assigned rides
Update ride status with controlled transitions:
accepted → ongoing / cancelled
ongoing → completed
Availability resets after ride completion/cancellation
🛠️ Admin
Add new drivers
View all rides in the system
Filter available drivers by district
Manually assign drivers to pending rides
🧰 Tech Stack
Python
Django 6.0.3
Django REST Framework 3.17
SQLite (local database)
Postman (API testing)
🗂️ Project Structure
enviornment11/          # Python virtual environment
└── rider_web/
    ├── rider_app/      # Core app (models, views, serializers, urls)
    └── rider_web/      # Project config (settings, urls)

Admin Credentials
Email: admin111@gmail.com
Password: 111

⚠️ Note: This setup is not secure and should not be used in production.

⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/your-username/ride-share-api.git
cd ride-share-api
2. Create virtual environment
python -m venv env
source env/bin/activate   # On Windows: env\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Run migrations
python manage.py makemigrations
python manage.py migrate
5. Start the server
python manage.py runserver
