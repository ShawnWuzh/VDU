from django.contrib import admin
from .models import Category,UserProfile,Connection,Video,VideoViews
# Register your models here.

admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Connection)
admin.site.register(Video)
admin.site.register(VideoViews)