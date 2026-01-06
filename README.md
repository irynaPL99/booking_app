# Booking App API

A simple REST API for a booking platform (similar to Airbnb).  
Built with Django, Django REST Framework, and MySQL.

## Features

- User registration and login (roles: owner or customer)
- Token authentication
- Custom permissions (owners edit only their own listings)
- Owners can create, update, and manage their listings
- All users can search and view active listings (with filters, search, and sorting)
- All listings have rating
- Bookings management
- Reviews system (one review per user per listing)
- Reviews for a specific listing: `/listings/{id}/reviews/` 

## Roles and Business Logic
### Guest (not logged in)
- View all active listings: `GET /listings/`
- View listing details: `GET /listings/{id}/`
- View reviews for listing: `GET /listings/{id}/reviews/`
- Cannot create bookings or reviews

### Customer (logged in)
- Create bookings: `POST /bookings/`
- View own bookings: `GET /bookings/`
- Write one review per listing: `POST /reviews/`
- View own reviews: `GET /reviews/my/`

### Owner (logged in)
- Create/update/delete own listings: `POST/PUT/DELETE /listings/`
- View own listings: `GET /listings/my/`
- View reviews for own listings: `GET /reviews/owner/`
- Manage bookings for own listings

## Tech Stack

- Python 3 / Django
- Django REST Framework
- MySQL database
- django-filters (for listing filters)
- Token authentication

## Project Structure
booking_app/
├── bookingapp/
│ ├── init.py
│ ├── settings.py # Django settings, DRF config
│ ├── urls.py # Main API router
│ └── wsgi.py
├── bookingapp/urls/ # App routers
│ ├── init.py
│ ├── auth.py # /auth/register, /auth/token
│ ├── booking.py
│ ├── listing.py
│ ├── review.py
│ └── user.py
├── bookingapp/views/ # API views
│ ├── auth.py # RegisterView, TokenLoginView
│ ├── booking.py
│ ├── listing.py
│ └── user.py # UserViewSet with /me/
├── bookingapp/serializers/ # Data serializers
│ ├── init.py
│ ├── authtoken.py
│ ├── booking.py
│ ├── changepassword.py
│ ├── listing.py
│ ├── review.py
│ └── user.py
├── booking_app/models/    # Database models
│ ├── init.py
│ ├── booking.py
│ ├── listing.py
│ └── review.py
├── manage.py
├── requirements.txt
└── README.md



## Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/irynaPL99/booking_app.git
   cd booking_app

2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or
venv\Scripts\activate          # Windows

3. Install dependencies
pip install -r requirements.txt

4. Configure MySQL database
Create a database in MySQL and update DATABASES in booking_app/settings.py with your credentials.

5. Run migrations
python manage.py makemigrations
python manage.py migrate

6. Create superuser (optional, for admin panel)
python manage.py createsuperuser

7. Run the development server
python manage.py runserver

8. 




## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/listings/` | GET | No | List active listings (filter, search, sort) |
| `/listings/{id}/` | GET | No | Listing details |
| `/listings/{id}/reviews/` | GET | No | Reviews for listing |
| `/listings/my/` | GET/POST | Yes | Owner's listings |
| `/bookings/` | GET/POST | Yes | Manage bookings |
| `/reviews/` | GET/POST | Yes | Manage reviews |
| `/reviews/my/` | GET | Yes | Own reviews |
| `/reviews/owner/` | GET | Yes | Reviews for owner's listings |
| `/auth/register/` | POST | No | Register user |
| `/auth/token/` | POST | No | Login, get token |
| `/auth/logout/` | POST | Yes | Delete token |

**Auth header**: `Authorization: Token your_token_here`

## Docker Setup

1. Build and run:
   ```bash
   docker-compose -f docker-compose.yml up -d

2. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser

3. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser

4. API ready at http://127.0.0.1:8000/api/v1/

## Local Setup (without Docker)

1. Clone repo:
   ```bash
   git clone https://github.com/irynaPL99/booking_app.git
   cd booking_app

2. Virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows

3. Install:
   ```bash
   pip install -r requirements.txt

4. MySQL database (update `settings.py`):
   ```bash
   python manage.py makemigrations
   python manage.py migrate

5. Run:
   ```bash
   python manage.py runserver

Test with Postman: register → get token → use in Authorization: Token ...



