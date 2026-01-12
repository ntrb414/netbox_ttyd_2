from django.urls import path
from . import views

urlpatterns = [
    path('device/<int:pk>/', views.DeviceTtyd2View.as_view(), name='device_ttyd_2'),
]
