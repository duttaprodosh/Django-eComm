from django.db import models

from django.db import models
from django.contrib.auth.models import User
from ecommerceapp.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime



class ShippingAddress(models.Model):
    shipping_id = models.AutoField(primary_key=True)
    id          = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_phone = models.CharField(max_length=255, null=True, blank=True)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    # Don't pluralize address
    class Meta:
        verbose_name_plural = "Shipping Address2"

    def __str__(self):
        return f"ShippinAddress - {str(self.id)}"


# Create a user Shipping Address by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()



# Automate the profile thing
post_save.connect(create_shipping, sender=User)

@receiver(pre_save, sender=ShippingAddress)
def set_id_on_update(sender, instance, **kwargs):
	if instance.pk:
		obj = sender._default_manager.get(pk=instance.pk)
		if obj.id == 1:
			instance.id = obj.shipping_id



