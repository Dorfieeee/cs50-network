
from django.urls import path

from . import views

app_name = "network"

urlpatterns = [
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<slug:slug>", views.ProfileDetailView.as_view(), name="profile-detail"),
    path("", views.index, name="index"),
]
