
from django import forms



class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={"class":'form-control',"placeholder":'Comment*',"rows":"8"}))