from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
