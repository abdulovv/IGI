from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileUpdateForm
from apps.core.models import Order


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('content:home')


def logout_view(request):
    logout(request)
    return redirect('content:home')


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешно завершена. Теперь вы можете войти.')
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем заказы только для обычных пользователей
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            context['user_orders'] = Order.objects.filter(customer=self.request.user).order_by('-created_at')
        context['user_timezone'] = self.request.session.get('user_timezone', 'Europe/Minsk')
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Профиль успешно обновлен')
        return super().form_valid(form)
