from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import Posts, Upvotes


def get_posts(user, *args, **kwargs):
    following_only = kwargs.get("following_only", False)
    single_user = kwargs.get("single_user", False)
    id = kwargs.get("id", False)

    if not id:
        queryList = Posts.objects.order_by(
            '-created')
        if following_only:
            queryList = queryList.filter(author__followers__follower=user)
        if single_user:
            queryList = queryList.filter(author__username__exact=single_user)
    else:
        queryList = Posts.objects.filter(pk=id)

    user_liked_posts = [
        like.post for like in Upvotes.objects.filter(user=user)]
    posts = []

    for post in queryList:
        _post = post.serialize()
        _post["userIsAuthor"] = post.author == user
        _post["userLikesThis"] = post in user_liked_posts
        posts.append(_post)

    return posts


def is_valid_or_error(model):
    '''Returns True if all fields are valid otherwise error'''
    try:
        model.full_clean()
    except ValidationError as e:
        return e

    return True


def get_object_or_false(pk, model):
    '''
    Returns Model object or False
    '''
    try:
        obj = model.objects.get(pk=pk)
    except ObjectDoesNotExist as e:
        return False

    return obj


def parseParams(params: dict) -> str:
    '''
    Parses dict key-value pairs into URL query format

    eg. {"page": 1, "recent": True} -> "?page=1&recent=true"
    '''
    q = ""
    c = 0
    for key in params:
        if c == 0:
            q += "?"
        else:
            q += "&"

        value = str(params[key]) if not type(
            params[key]) == "bool" else str(params[key]).lower()
        q += key + "=" + value
        c += 1

    return q
