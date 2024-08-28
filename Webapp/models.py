import datetime

from asgiref.sync import async_to_sync
from django.db import models
from django.utils import timezone


# Create your models here.
class Mechanics(models.Model):
    Mechid = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    Age = models.IntegerField(null=True, blank=True)
    Address = models.CharField(max_length=100, null=True, blank=True)
    Mobile = models.IntegerField(null=True, blank=True)
    Vehicle = models.CharField(max_length=100, null=True, blank=True)
    Place = models.CharField(max_length=100, null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Username = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    Picture = models.ImageField(upload_to='Mechanic Images', null=True, blank=True)
    Type = models.CharField(max_length=100, null=True, blank=True)


class logintable(models.Model):
    Username = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    Type = models.CharField(max_length=100, null=True, blank=True)


class ServiceCenter(models.Model):
    # Serviceid=models.AutoField(primary_key=True)
    BName = models.CharField(max_length=100, null=True, blank=True)
    CPerson = models.CharField(max_length=100, null=True, blank=True)
    Age = models.IntegerField(null=True, blank=True)
    Address = models.CharField(max_length=100, null=True, blank=True)
    City = models.CharField(max_length=100, null=True, blank=True)
    State = models.CharField(max_length=100, null=True, blank=True)
    PIN = models.IntegerField(null=True, blank=True)
    Mobile = models.IntegerField(null=True, blank=True)
    Description = models.CharField(max_length=100, null=True, blank=True)
    Hours = models.CharField(max_length=100, null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Username = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    Picture = models.ImageField(upload_to='Service Center Images', null=True, blank=True)
    Type = models.CharField(max_length=100, null=True, blank=True)


class feedback(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    message = models.CharField(max_length=100, null=True, blank=True)


class userdatas(models.Model):
    Userid = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Mobile = models.IntegerField(null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Location = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    Cpassword = models.CharField(max_length=100, null=True, blank=True)


class Service(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    service = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)






class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(userdatas, on_delete=models.CASCADE,default=1)
    uname = models.CharField(max_length=100, null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Phone = models.IntegerField(null=True, blank=True)
    Address = models.CharField(max_length=500, null=True, blank=True)
    Message = models.CharField(max_length=500, null=True, blank=True)
    Totalprice = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


class Cart(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    Productname = models.CharField(max_length=100, null=True, blank=True)
    Quantity = models.IntegerField(null=True, blank=True)
    Totalprice = models.IntegerField(null=True, blank=True)
    order_id = models.ForeignKey('Order', related_name='cart_items', on_delete=models.CASCADE,default=1)

class UserRequests(models.Model):
    Userid = models.ForeignKey(userdatas, on_delete=models.CASCADE)
    Mechid = models.ForeignKey(Mechanics, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)


class Mechpayment(models.Model):
    Userid = models.IntegerField(null=True, blank=True)
    Mechid = models.IntegerField(null=True, blank=True)
    Reqid = models.IntegerField(null=True, blank=True)
    Amount = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)


class PINLocation(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    pin_code = models.CharField(max_length=10)


class Booking(models.Model):
    user = models.ForeignKey(userdatas, on_delete=models.CASCADE)
    service_center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE)  # Assuming ServiceCenter model exists
    date_booked = models.DateTimeField(default=datetime.datetime.now())
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=100, null=True, blank=True)


class servicefeedback(models.Model):
    userid = models.IntegerField(null=True, blank=True)
    serid = models.IntegerField(null=True, blank=True)
    feedback = models.CharField(max_length=500, null=True, blank=True)


class Chat(models.Model):
    user_question = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_question


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question









