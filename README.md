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
- django-filters
- Token authentication

## Project Structure

```text
booking_app/
├── booking_app/
│   ├── admin.py
│   ├── apps.py
│   ├── choices.py
│   ├── permissions.py
│   ├── routers.py
│   │
│   ├── migrations/
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── booking.py
│   │   ├── listing.py
│   │   ├── review.py
│   │   └── user.py
│   │
│   ├── serializers/
│   │   ├── auth.py
│   │   ├── auth_token.py
│   │   ├── booking.py
│   │   ├── change_password.py
│   │   ├── listing.py
│   │   ├── review.py
│   │   └── user.py
│   │
│   ├── urls/
│   │   ├── auth.py
│   │   ├── booking.py
│   │   ├── listing.py
│   │   ├── review.py
│   │   └── user.py
│   │
│   └── views/
│       ├── auth.py
│       ├── booking.py
│       ├── listing.py
│       ├── review.py
│       └── user.py
│
├── core/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env                 # NOT in Git
├── .env_example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

## Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/irynaPL99/booking_app.git
   cd booking_app
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

