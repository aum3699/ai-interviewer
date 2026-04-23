from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_personality, name='analyze'),
    path('device_analysis/', views.device_analysis, name='device_analysis'),
    path('api/usage/', views.api_usage, name='api_usage'),
    path('api/device_analysis/', views.api_device_analysis, name='api_device_analysis'),
    path('api/check_mobile_data/', views.check_mobile_data, name='check_mobile_data'),
]