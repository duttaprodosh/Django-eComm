from django.urls import path, include
from . import views
urlpatterns = [
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('forget_password/', views.forget_password, name="forget_password"),
    path('update_password_emaillink/<str:userid>/<str:token>/', views.update_password_emaillink, name='update_password_emaillink'),
    path('update_password/', views.update_password, name='update_password'),
    path('user_profile/', views.user_profile, name='user_profile'),
]