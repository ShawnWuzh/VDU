from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType

# Create your models here.

def upload_location(instance,filename):
    CurrentModel = instance.__class__
    new_id = CurrentModel.objects.order_by("id").last().id + 1
    return "%s/%s" % (new_id,filename)

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to=upload_location,blank=True)
    description = models.TextField(null=True,blank=True)

    def get_connections(self):
        connections = Connection.objects.filter(creator=self.user)
        return connections
    def get_followers(self):
        followers = Connection.objects.filter(following=self.user)
        return followers

    def __str__(self):
        return self.user.username

class Connection(models.Model):
    created = models.DateTimeField(auto_now_add=True,editable=False)
    creator = models.ForeignKey(User,related_name="friendship_creator_set")
    following = models.ForeignKey(User,related_name="friend_set")

class Video(models.Model):
    title = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category,default='Unknown')
    tags = models.CharField(max_length=120)
    audience = models.CharField(max_length=20)
    description = models.TextField()
    url = models.URLField()
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True,auto_now=False)
    editors_pick = models.BooleanField(default=False)
    class Meta:
        ordering = ['-time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("videos:videodetail",kwargs={"slug":self.slug})

    @property
    def comment(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

class VideoViews(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    time = models.DateTimeField(auto_now_add=True,auto_now=False)
    ip = models.GenericIPAddressField(null=True,blank=True)

def create_slug(instance):
    slug = slugify(instance.title)
    slug = slug + str(Video.objects.order_by("id").last().id + 1)
    return slug

def pre_save_post_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver,sender=Video)







