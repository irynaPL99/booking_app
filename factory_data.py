import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import factory
from faker import Faker
from django.contrib.auth.hashers import make_password
from django.utils import timezone


from booking_app.models import (
    User,
    Booking,
    Listing,
    Review

)

faker_ = Faker()
