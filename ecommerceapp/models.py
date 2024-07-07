from django.shortcuts import render, redirect
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


# Create Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100, blank=True)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

# There are four signals - pre_save, post_save, pre_delete, post_delete
# Automate the profile thing
post_save.connect(create_profile, sender=User)

class Contact(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    desc = models.CharField(max_length=200, blank=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True, default="")
    subcategory = models.CharField(max_length=20, blank=True, default="")
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=15)
    desc = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='images')
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=15)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    oid=models.CharField(max_length=150,blank=True)
    amountpaid=models.CharField(max_length=500,blank=True,null=True)
    paymentstatus=models.CharField(max_length=20,blank=True)
    phone = models.CharField(max_length=100,default="")
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    invoice_no = models.CharField(max_length=250, default=None, null=True)
    invoice_date = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.name


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    update_desc = models.CharField(max_length=5000)
    delivered=models.BooleanField(default=False)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."


# Auto Add shipping Date
@receiver(pre_save, sender=Orders)
def set_shipped_date_on_update(sender, instance, **kwargs):
	if instance.pk:
		now = datetime.datetime.now()
		obj = sender._default_manager.get(pk=instance.pk)
		if instance.shipped and not obj.shipped:
			instance.date_shipped = now



# Create Order Items Model
class OrderItem(models.Model):
    # Foreign Keys
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'
