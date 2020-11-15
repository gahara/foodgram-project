from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = '/auth/login/'
    template_name = 'signup.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        send_mail(
            'Регистрация на сайте foodgram',
            'Вы зарегистритрированы успешно',
            'example.com <admin@example.com>',
            [email],
            fail_silently=False
        )
        return super().form_valid(form)
