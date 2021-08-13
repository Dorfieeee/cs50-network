
from django.urls import path
from django.contrib.auth.decorators import login_required


from . import views

app_name = "network"

urlpatterns = [
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<slug:slug>", login_required(views.ProfileDetailView.as_view()), name="profile-detail"),
    path("/user/<slug:slug>/image", login_required(views.ProfileImage.as_view()), name="profile-image"),
    path("", views.index, name="index"),
]
