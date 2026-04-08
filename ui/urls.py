from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('coverage/', views.coverage, name='coverage'),
    path('api/search', views.search_trips, name='search_trips'),
    path('api/stations', views.get_stations, name='get_stations'),
]
