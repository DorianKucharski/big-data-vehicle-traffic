"""
  Przekierowania.
"""

from django.urls import include, path
from . import views

urlpatterns = [
  path('get_raw', views.get_raw),
  path('get_all', views.get_all),
  path('by_hours', views.by_hours),
  path('by_days_of_week', views.by_days_of_week),
  path('by_days_of_month', views.by_days_of_month),
  path('by_months', views.by_months),
  path('real_time', views.real_time)
]