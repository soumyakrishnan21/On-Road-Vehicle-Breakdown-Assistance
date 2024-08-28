from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils import timezone
import pytz
utc_time = timezone.now()  # Or any other timezone-aware datetime object

# Define the target time zone
ist_timezone = pytz.timezone('Asia/Kolkata')

# Convert UTC to IST
ist_time = utc_time.astimezone(ist_timezone)
print("IST Time:", ist_time)
now_utc = timezone.now()  # Gets the current time in UTC
now_local = timezone.localtime(now_utc)
# Create your models here.
class Category(models.Model):
    Categoryname=models.CharField(max_length=100,blank=True,null=True)
    Image=models.ImageField(upload_to="Category Images",blank=True,null=True)
    Description=models.CharField(max_length=100,blank=True,null=True)

class Products(models.Model):
    Productname=models.CharField(max_length=100,blank=True,null=True)
    Category=models.CharField(max_length=100,blank=True,null=True)
    Price=models.IntegerField(blank=True,null=True)
    Image = models.ImageField(upload_to="Product Images", blank=True, null=True)
    Description = models.CharField(max_length=500, blank=True, null=True)
class chatmessage(models.Model):
    room_name = models.CharField(max_length=100)
    sender_type = models.CharField(max_length=50)
    sender_id = models.IntegerField()
    receiver_type = models.CharField(max_length=50)
    receiver_id = models.IntegerField()
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now())  # Use callable timezone.now
