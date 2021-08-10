
from django.urls import path

from .rest_views import PostsAPI, UpvotesAPI, FollowersAPI, FollowerAPI

app_name = "network-api"

urlpatterns = [
    # LIKE ROUTES
    #
    path("posts/<int:post_id>/like", UpvotesAPI.as_view(), name="post-like-api"),
    # POSTS ROUTES   
    # 
    path("posts/<int:post_id>/", PostsAPI.as_view(), name="post-detail-api"),
    #  
    path("posts/", PostsAPI.as_view(), name="posts-api"),
    # FOLLOW ROUTES
    #
    path("followers/<str:followee>/", FollowerAPI.as_view(), name="follower-api"),
    #
    path("followers/", FollowersAPI.as_view(), name="followers-api"),
]