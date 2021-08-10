import json
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator

from .models import Posts, User, Followers
from .helpers import get_posts, is_valid_or_error, get_object_or_false, parseParams


class PostsAPI(View):

    def get(self, request):
        ''' Get posts '''
        response = {}
        params = {}

        page_num = int(request.GET.get('page', 1))
        response["currPage"] = page_num

        single_user = request.GET.get('singleUser', False)
        if single_user:
            params["singleUser"] = single_user


        following_only = request.GET.get('following', False)
        if following_only == "true":
            following_only = True
            params["following"] = "true"

        posts = get_posts(request.user, following_only=following_only, single_user=single_user)
        
        p = Paginator(posts, 10)
        page = p.page(page_num)

        response["posts"] = page.object_list
        response["pageCount"] = p.num_pages
        if page.has_next():
            params["page"] = page_num + 1
            response["nextPage"] = f'{reverse("network-api:posts-api")}{parseParams(params)}'
        if page.has_previous():
            params["page"] = page_num - 1
            response["prevPage"] = f'{reverse("network-api:posts-api")}{parseParams(params)}'

        return JsonResponse(response, safe=False)

    @method_decorator(login_required)
    def post(self, request):
        ''' Create new post '''
        data = json.loads(request.body)
        post_body = data.get('postBody', "")
        new_post = Posts(body=post_body, author=request.user)

        e = is_valid_or_error(new_post)
        if e is True:
            new_post.save()
            return JsonResponse({"msg": "Post was added successfully"})
        else:
            return JsonResponse({"error": dict(e)})
    
    @method_decorator(login_required)
    def delete(self, request, post_id):
        ''' Delete post '''
        post = get_object_or_false(post_id, Posts)
        if post is not False:
            if post.author.id == request.user.id:
                post.delete()
                return JsonResponse({"msg": "Post was deleted successfully"})
            else:
                return JsonResponse({"error": ["User not authorized",
                                            "User has to be author of the post"]}, status=401)
        else:
            return JsonResponse({"error": "Post does not exist"}, status=404)

    @method_decorator(login_required)
    def put(self, request, post_id):
        ''' Edit post '''
        edited_body = json.loads(request.body)

        if len(edited_body) < 1:
            return JsonResponse({"error": "Post must be longer than 0 chars"}, status=400)

        post = get_object_or_false(post_id, Posts)
        if post is not False:
            if post.author.id == request.user.id:
                # update here
                post.body = edited_body
                post.save()
                return JsonResponse({"msg": "Post was edited successfully"})
            else:
                return JsonResponse({"error": ["User not authorized",
                                            "User has to be author of the post"]}, status=401)
        else:
            return JsonResponse({"error": "Post does not exist"}, status=404)


# ---------------------------------------------------------


class FollowersAPI(View):
    @method_decorator(login_required)
    def get(self, request):
        pass

class FollowerAPI(View):
    @method_decorator(login_required)
    def delete(self, request, followee):
        follower = request.user
        followee = User.objects.filter(username=followee)
        if (followee.exists()):
            Followers.objects.filter(follower=follower, followee=followee.first()).delete()
        else:
            return JsonResponse({"error": "Requested user to be removed from your following list does not exist"}, status=400)
        
        return JsonResponse({"msg": "User was successfully removed from your following list"})

    @method_decorator(login_required)
    def post(self, request, followee):
        follower = request.user
        followee = User.objects.filter(username=followee)
        if (followee.exists()):
            followee = followee.first()
            if follower is followee:
                return JsonResponse({"error": "Users cannot follow themselves O.o"}, status=400)
            if Followers.objects.filter(follower=follower, followee=followee).exists():
                return JsonResponse({"error": "User " + followee.username + " is already in your following list"}, status=400)

            relation = Followers(follower=follower, followee=followee)
            relation.save()
        else:
            return JsonResponse({"error": "Requested user to be added to your following list does not exist"}, status=400)
        
        return JsonResponse({"msg": "User was successfully added to your following list"})


class UpvotesAPI(View):
    
    @method_decorator(login_required)
    def post(self, request, post_id):
        ''' Create like '''
        post=get_object_or_false(post_id, Posts)
        # first check if such post exists
        if post is not False:
            user_likes_this=False
            # prevent user from liking his own post
            if request.user.id != post.author.id:
                post_likes=post.upvotes_set.all()
                # check if like from this user does not exist already
                if not post_likes.filter(post=post_id, user=request.user.id).exists():
                    # finally, create like
                    post.upvotes_set.create(user=request.user)
                    number_of_likes=post_likes.count()
                    user_likes_this=True
                    return JsonResponse({"msg": "Success", "userLikesThis": user_likes_this, "numberOfLikes": number_of_likes })
                else:
                    user_likes_this=True
                    return JsonResponse({"error": "User already likes this post", "userLikesThis": user_likes_this}, status=400)
            else:
                return JsonResponse({"error": "User can not like his own post", "userLikesThis": user_likes_this}, status=401)
        else:
            return JsonResponse({"error": "Post was not found"}, status=400)

        
    @method_decorator(login_required)
    def delete(self, request, post_id):
        ''' Delete like '''
        post=get_object_or_false(post_id, Posts)
        # first check if such post exists
        if post is not False:
            post_likes=post.upvotes_set.all()
            # check if like from this user does exist already
            if post_likes.filter(post=post_id, user=request.user.id).exists():
                # finally, delete like
                post_likes.get(post=post_id, user=request.user.id).delete()
                number_of_likes=post_likes.count()
                user_likes_this=False
                return JsonResponse({"msg": "Success", "userLikesThis": user_likes_this, "numberOfLikes": number_of_likes })
            else:
                user_likes_this=False
                return JsonResponse({"error": "User has not liked this post yet", "userLikesThis": user_likes_this}, status=400)

        else:
            return JsonResponse({"error": "Post was not found"}, status=400)