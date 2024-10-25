from django.urls import path

from spotify.views import favicon

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("rate", views.rate, name="rate"),
    path("favicon.ico", favicon, name="favicon"),
]
