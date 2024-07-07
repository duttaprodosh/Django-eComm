from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views


urlpatterns = [
    path('checkout/', views.checkout, name="checkout"),
    path('shipped_dash', views.shipped_dash, name="shipped_dash"),
    path('not_shipped_dash', views.not_shipped_dash, name="not_shipped_dash"),
    path('payment_orders/<int:pk>', views.payment_orders, name='payment_orders'),
############################################# # Begin: PAYMENT INTEGRATION  ##########################
    #path('handlerequest/', views.handlerequest, name="handlerequest"),
############################################# # End  : PAYMENT INTEGRATION  ##########################
]