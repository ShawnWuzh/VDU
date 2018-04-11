from django.shortcuts import render,get_object_or_404,redirect
from .models import Video,UserProfile,VideoViews,Connection
from .forms import UserForm, UserProfileForm, VideoUploadForm,UserLoginForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib import messages
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ipware import get_client_ip
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.db.models import F,Count
from django.utils import timezone as datetime
from django.urls import reverse
# Create your views here.

def get_videos_views(videos_list):
    video_views = {}
    reference = {}
    video_views_all_time = VideoViews.objects.all().\
        values('video').annotate(views=Count('ip'))
    for dicts in video_views_all_time:
        reference[dicts['video']] = dicts['views']
    for video_dict in videos_list:
        if video_dict['video'] not in reference:
            video_views[Video.objects.get(id=video_dict['video'])] = 0
        else:
            video_views[Video.objects.get(id=video_dict['video'])] = reference[video_dict['video']]
    return video_views

def get_views(videos):
    video_views = {}
    reference = {}
    video_views_all_time = VideoViews.objects.all().\
        values('video').annotate(views=Count('ip'))
    for dicts in video_views_all_time:
        reference[dicts['video']] = dicts['views']
    for video in videos:
        if video.id not in reference:
            video_views[video] = 0
        else:
            video_views[video] = reference[video.id]
    return video_views


def index(request):
    one_day_before_time = datetime.datetime.now() - datetime.timedelta(days=1)
    days_popular_videos = get_videos_views(VideoViews.objects.filter(time__gte=one_day_before_time).\
        values('video').annotate(daily_views=Count('ip')).order_by('-daily_views')[:5])
    one_week_before_time = datetime.datetime.now() - datetime.timedelta(days=7)
    week_popular_videos = get_videos_views(VideoViews.objects.filter(time__gte=one_week_before_time).\
        values('video').annotate(week_views = Count('ip')).order_by('-week_views')[:5])
    one_hour_before_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    trending_videos = get_videos_views(VideoViews.objects.filter(time__gte=one_hour_before_time). \
        values('video').annotate(hour_views = Count('ip')).order_by('-hour_views')[:2])
    latest_videos = get_views(Video.objects.all().order_by('-time')[:4])
    one_month_before_time = datetime.datetime.now() - datetime.timedelta(days=30)
    editors_first_pick = get_views(Video.objects.filter(editors_pick__exact=True).order_by('-time')[:1])
    editors_other_pick = get_views(Video.objects.filter(editors_pick__exact=True).order_by('-time')[1:5])
    context = {
        'days_popular_videos':days_popular_videos,
        'week_popular_videos':week_popular_videos,
        'trending_videos':trending_videos,
        'latest_videos':latest_videos,
        'editors_other_pick':editors_other_pick,
        'editors_first_pick':editors_first_pick
    }
    return render(request,'index.html',context)

@login_required
def video_upload(request):
    form = VideoUploadForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        userprofile = UserProfile.objects.get(user=request.user)
        instance.author = userprofile
        instance.save()
        messages.success(request,"Successfully Uploaded!")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form":form,
    }
    return render(request,"upload.html",context)

def video_detail(request,slug):
    instance = get_object_or_404(Video,slug=slug)
    initial_data = {
        "content_type":instance.get_content_type,
        "object_id":instance.id,
    }
    if request.user.is_authenticated:
        view_user = request.user
    else:
        view_user = None
    client_ip = get_client_ip(request)
    user_view = VideoViews(user=view_user,ip=client_ip,video=instance)
    user_view.save()
    views_set = VideoViews.objects.filter(video=instance)
    if views_set:
        views = views_set.count()
    else:
        views = 0
    author = instance.author.user
    followers_set = Connection.objects.filter(following=author)
    if followers_set:
        followers = followers_set.count()
    else:
        followers = 0
    tags = instance.tags.split(',')
    form = CommentForm(request.POST or None, initial = initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get('object_id')
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment,created = Comment.objects.get_or_create(
                                    user=request.user,
                                    content_type = content_type,
                                    object_id= obj_id,
                                    content=content_data,
                                    parent=parent_obj
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    comments = instance.comment
    context = {
        "instance":instance,
        "comments":comments,
        "views":views,
        "comment_form":form,
        'followers':followers,
        'tags':tags
    }
    return render(request,'video_detail.html',context=context)

def video_list(request,category=None):
    if category:
        queryset_list = Video.objects.filter(category__name__iexact=category).exclude(audience__iexact="private")
    else:
        queryset_list = Video.objects.all().exclude(audience__iexact="private")
    paginator = Paginator(queryset_list,18)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "object_list":get_views(queryset),
        "page_request_var":page_request_var,
        "category":category,
        "page_list":queryset,
    }
    return render(request,"video_list.html",context)

@login_required
def video_delete(request,slug=None):
    instance = get_object_or_404(Video,slug=slug)
    instance.delete()
    messages.success(request,"Successfully Deleted")
    return redirect("videos:list_user_videos")
## this form is register for a user

def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        user_profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and user_profile_form.is_valid():
            password = user_form.cleaned_data['password']
            user = user_form.save()
            user.set_password(password)
            user.save()
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            user.save()
            return redirect("videos:login")
        else:
            print(user_form.errors,user_profile_form.errors)
    else:
        user_form = UserForm()
        user_profile_form = UserProfileForm()
    context = {
        'user_form':user_form,
        'user_profile_form':user_profile_form,
    }
    return render(request,'register.html',context=context)

def login_view(request):
    next = request.GET.get("next")
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        login(request,user)
        print("login successfully!")
        if next:
            return redirect(next)
        return redirect("videos:index")
    print("fail to login")
    context = {
        "form":form,
    }

    return render(request,"signin.html",context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('/index')


def follow(request,slug):
    following = User.objects.get(username=slug)
    creator = request.user
    Connection.objects.create(creator=creator,following=following)
    messages.success(request, "Successfully Followed!")
    return redirect(reverse('user',kwargs={"slug":slug}))

def unfollow(request,slug):
    following = User.objects.get(username=slug)
    creator = request.user
    connection = Connection.objects.get(creator=creator,following=following)
    messages.success(request,"Successfully Unfollowed!")
    connection.delete()
    return redirect(reverse('user',kwargs={"slug":slug}))

def user_homepage(request,slug):
    user = User.objects.get(username=slug)
    owner = False
    if request.user == user:
        owner = True
    userprofile = UserProfile.objects.get(user=user)
    followers = Connection.objects.filter(following=user)
    context = {
        "userprofile":userprofile,
        "followers":followers,
        "owner":owner,
    }
    return render(request,"user_homepage.html",context=context)

def user_videos(request,slug):
    user = User.objects.get(username=slug)
    userprofile = UserProfile.objects.get(user=user)
    followers = Connection.objects.filter(following=user)
    if request.user == user:
        videos = Video.objects.filter(author=userprofile)
    else:
        videos = Video.objects.filter(author=userprofile).filter(audience__iexact="public")
    paginator = Paginator(videos,18)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    videos_set = get_views(queryset)
    context = {
        "userprofile":userprofile,
        "videos":videos_set,
        'followers':followers,
        'page_list':queryset
    }
    return render(request,"user_videos.html",context=context)





