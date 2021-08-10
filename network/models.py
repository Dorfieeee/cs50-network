from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls.base import reverse
from django.utils.formats import date_format


class User(AbstractUser):

    def __str__(self) -> str:
        return self.email


class Followers(models.Model):
    # the one who follows
    follower = models.ForeignKey(
        to=User, on_delete=CASCADE, related_name="follows")
    # the one who is followed
    followee = models.ForeignKey(
        to=User, on_delete=CASCADE, related_name="followers")
    # when was relationship established
    created = models.DateTimeField('date created', auto_now_add=True)

    def __str__(self) -> str:
        return self.follower.username + " -> " + self.followee.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    slug = models.SlugField("profile url")
    dob = models.DateTimeField('date of birth', null=True, blank=True)
    avatar_slug = models.SlugField("profile img url", null=True, blank=True)

    def __str__(self) -> str:
        return self.user.email


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        slug = reverse("network:profile-detail", kwargs={"slug": instance.username})
        Profile.objects.create(user=instance, slug=slug)
    pass


class Posts(models.Model):
    author = models.ForeignKey(User, on_delete=CASCADE)
    body = models.TextField(max_length=1000, blank=False)
    created = models.DateTimeField('date created', auto_now_add=True)
    #edited = models.DateTimeField('date edited', auto_now=True)

    def __str__(self) -> str:
        return self.author.username + " @ [" + date_format(self.created, "DATETIME_FORMAT") + "]"


class Upvotes(models.Model):
    # Any user can upvote any post
    user = models.ForeignKey(User, on_delete=CASCADE)
    post = models.ForeignKey(Posts, on_delete=CASCADE)
    created = models.DateTimeField('date created', auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username + "->" + self.post.__str__()


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    post = models.ForeignKey(Posts, on_delete=CASCADE)
    body = models.TextField(max_length=1000)
    created = models.DateField('date created', auto_now_add=True)

    def __str__(self) -> str:
        return self.body[0:10] + "->" + self.post.__str__()
