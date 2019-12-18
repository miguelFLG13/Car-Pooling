from django.conf.urls import include
from django.urls import path

from journey import views


urlpatterns = [
    path(
        'status/',
        views.StatusAPIView.as_view(),
        name='get_status'
    ),
    path(
        'cars/',
        views.CarAPIView.as_view(),
        name='put_cars'
    ),
    path(
        'journey/',
        views.JourneyAPIView.as_view(),
        name='post_journey'
    ),
    path(
        'dropoff/',
        views.DropOffAPIView.as_view(),
        name='post_dropoff'
    ),
    path(
        'locate/',
        views.LocateAPIView.as_view(),
        name='post_locate'
    ),
]
