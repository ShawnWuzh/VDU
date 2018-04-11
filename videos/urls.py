from django.conf.urls import url
from . import views

app_name = 'videos'

urlpatterns = [
    url(r'index/$',views.index,name='index'),
    url(r'register/$',views.register,name='register'),
    url(r'login/$',views.login_view,name='login'),
    url(r'logout/$',views.logout_view,name='logout'),
    url(r'videos-list/(?P<category>[\w-]+)/$',views.video_list,name='videos'),
    url(r'video-detail/(?P<slug>[\w-]+)/$',views.video_detail,name='videodetail'),
    url(r'video-upload/$',views.video_upload,name='videoupload'),
    url(r'video-delete/(?P<slug>[\w-]+)/$',views.video_delete,name='videodelete'),
    url(r'user-profile/(?P<slug>[\w-]+)/$',views.user_homepage,name='userhomepage'),
    url(r'user-video/(?P<slug>[\w-]+)/$',views.user_videos,name='uservideos'),
]