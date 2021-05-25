"""
  Przekierowania.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),

    path('line_chart', views.line_chart),

    path('cars_in', views.cars_in),
    path('cars_out', views.cars_out),
    path('cars_all', views.cars_all),

    path('by_hours', views.by_hours),
    path('by_days_of_week', views.by_days_of_week),
    path('by_days_of_month', views.by_days_of_month),
    path('by_months', views.by_months),

    path('real_time', views.real_time),

    path('camera', views.camera),
]
