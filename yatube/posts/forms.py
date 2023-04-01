from django import forms
from django.contrib.auth import get_user_model

from .models import Post


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        group = forms.ModelChoiceField(queryset=Post.objects.all(),
                                       required=False, to_field_name='group')
        widgets = {
            'text': forms.Textarea(),
        }

        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
