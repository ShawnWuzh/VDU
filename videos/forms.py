from django import forms
from .models import UserProfile,Video
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email","required":"required"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "password","required":"required"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password","required":"required"}))
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "first name","required":"required"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "last name","required":"required"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "username","required":"required"}),
        }

    def clean(self, *args, **kwargs):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm password does not match!"
            )



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'description',
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "description", "required": "required"}),
        }

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title',
            'category',
            'tags',
            'audience',
            'description',
            'file'
        ]
        CHOICES = (('Private', 'Private'), ('Public', 'Public'))

        widgets = {
            'title':forms.TextInput(attrs={"class":"title form-control","placeholder":"Video Name","id":"title"}),
            "category":forms.Select(attrs={"class":"category form-control","id":"category"}),
            "tags":forms.TextInput(attrs={"class":"tag form-control","placeholder":"Enter up to 5 tags and separate them with a coma"}),
            "audience": forms.Select(attrs={"class": "privacy form-control","id":"privacy"},choices=CHOICES),
            "description":forms.Textarea(attrs={"class":"description form-control","placeholder":"Description","id":"description"}),
            "file": forms.FileInput(attrs={"class": "file form-control", "placeholder": "file", "id": "file", "name":"file"}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"input form-control","placeholder":"username","required":"required"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"input form-control","placeholder":"password","required":"required"}))

    def clean(self,*args,**kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username,password=password)
            if not user:
                raise forms.ValidationError("The user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password")
        return super(UserLoginForm, self).clean(*args,**kwargs)





