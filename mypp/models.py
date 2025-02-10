from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('traveller', 'Traveller')], default='traveller')
    
    def __str__(self):
        return self.username
    
class Place(models.Model):
    name = models.CharField(max_length=200)
    images = models.JSONField(blank=True, null=True)
    description = models.TextField()
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    tips = models.JSONField(default=list)
    events = models.JSONField(default=list)

    def __str__(self):
        return self.name

from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    date = models.DateField()
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    first_name = models.CharField(max_length=100, default='John')  
    last_name = models.CharField(max_length=100, default='Doe')   
    phone = models.CharField(max_length=15, default='000-000-0000') 
    email = models.EmailField(max_length=50, default="example@gmail.com")       
    adults = models.PositiveIntegerField(default=1)   
    children = models.PositiveIntegerField(default=0) 
    trip_preferences = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def __str__(self):
        return f"Booking by {self.user.username} at {self.place.name}"

class TravelTip(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, choices=[
        ('General', 'General'),
        ('Cultural', 'Cultural'),
        ('Safety', 'Safety'),
        ('Budgeting', 'Budgeting'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Itinerary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    destinations = models.ManyToManyField('Place')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.place.name}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} rated {self.place.name} {self.rating}/5"