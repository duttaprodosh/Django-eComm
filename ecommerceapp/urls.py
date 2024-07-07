from django.urls import path, include
from ecommerceapp import views



urlpatterns = [
    path('', views.index, name="index"),
    path('contact/', views.contact, name="contact"),
    path('about/', views.about, name="about"),
    path('product/<int:pk>', views.product, name='product'),
    path('orders/<str:user_type>', views.orders, name='orders'),
    path('update_user_info/<str:update_token>', views.update_user_info, name='update_user_info'),
    path('invoice/<str:full_name>/<str:shipping_address>/<str:email>/<str:phone>/<str:invoice_no>/<str:invoice_date>/<str:order_no>/<str:totals>', views.invoice, name='invoice'),
    #path('profile',views.profile,name="profile"),
    #path('checkout/', views.checkout, name="Checkout"),
    #path('handlerequest/', views.handlerequest, name="HandleRequest"),
]