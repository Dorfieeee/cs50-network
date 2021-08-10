from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Count
from django.urls import reverse
from django.utils.formats import date_format

from .models import Posts, Upvotes, Followers

def get_posts(user, *args, **kwargs):
    following_only = kwargs.get("following_only", False)
    single_user = kwargs.get("single_user", False)
    id = kwargs.get("id", False)

    if not id:
        queryList = Posts.objects.order_by(
            '-created').annotate(number_of_likes=Count("upvotes"))
        if following_only:
            queryList = queryList.filter(author__followers__follower=user)
        if single_user:
            queryList = queryList.filter(author__username__exact=single_user)
    else:
        queryList = Posts.objects.filter(pk=id).annotate(number_of_likes=Count("upvotes"))


    user_liked_posts = [like.post for like in Upvotes.objects.filter(user=user)]
    posts = []

    for post in queryList:
        does_user_like_it = post in user_liked_posts
        is_user_author = post.author == user

        posts.append({
            "id": post.id,
            "author": {
                "id": post.author.id,
                "username": post.author.username
            },
            "body": post.body,
            "created": {
                "short": date_format(post.created, "d M"),
                "long": date_format(post.created, "DATETIME_FORMAT")
            },
            "numberOfLikes": post.number_of_likes,
            "userIsAuthor": is_user_author,
            "userLikesThis": does_user_like_it,
            "postURL": reverse("network-api:post-detail-api", args=[post.id]),
            "likeURL": reverse("network-api:post-like-api", args=[post.id]),
            "profileURL": post.author.profile.slug,
            })

    return posts

def is_valid_or_error(model):
    try:
        model.full_clean()
    except ValidationError as e:
        return e
    
    return True

def get_object_or_false(pk, model):
    try:
        obj = model.objects.get(pk=pk)
    except ObjectDoesNotExist as e:
        return False
    
    return obj

def parseParams(params):
    q = ""
    c = 0
    for key in params:
        if c == 0:
            q += "?"
        else:
            q += "&"

        q += key + "=" + str(params[key])      
        c += 1

    return q

    

