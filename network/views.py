from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.detail import DetailView

from .models import Profile, User

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("network:login"))

    return render(request, "network/home.html")


def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("network:login"))


    return render(request, "network/following.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("network:logout"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        if username in ["login", "logout", "register", "index", "admin"]:
            return render(request, "network/register.html", {
                "message": "This username is not allowed"
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "network/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['followers'] = [relation.follower for relation in context["profile"].user.followers.all()]
        context['follows'] = [relation.followee for relation in context["profile"].user.follows.all()]
        return context