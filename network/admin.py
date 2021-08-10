from django.contrib import admin
from .models import User, Followers, Upvotes, Comments, Profile, Posts


# Register your models here.
admin.site.register(Followers)
admin.site.register(User)
admin.site.register(Upvotes)
admin.site.register(Comments)
admin.site.register(Profile)
admin.site.register(Posts)