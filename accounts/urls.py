from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registeruser'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),
]
