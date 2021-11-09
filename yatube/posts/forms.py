from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if (text == '') or (text is None):
            raise forms.ValidationError('Напишите что-нибудь!')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    # В порядке эксперимента, который провалился:
    def clean_text(self):
        text = self.cleaned_data.get('text')
        forbidden_words = [
            'бля',
            'кумкват'
        ]
        separating_sybols = '.,/;:!?"'
        bold_text = text.lower()
        for char in separating_sybols:
            bold_text = bold_text.replace(char, ' ')
        for word in forbidden_words:
            if word in bold_text.split():
                raise forms.ValidationError('Ругаться нехорошо!')
        return text
