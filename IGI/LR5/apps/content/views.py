from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import News, CompanyInfo, FAQ, Review, Vacancy, Promotion, Employee
from .forms import ReviewForm
import calendar
from datetime import datetime, date
import pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

class HomeView(TemplateView):
    template_name = 'content/home.html'

    def generate_calendar(self):
        # Получаем временную зону пользователя или используем Минск по умолчанию
        user_timezone_str = self.request.session.get('user_timezone', 'Europe/Minsk')
        try:
            user_timezone = pytz.timezone(user_timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            user_timezone = pytz.timezone('Europe/Minsk')
            user_timezone_str = 'Europe/Minsk'

        # Получаем текущее время в указанной временной зоне
        now_utc = datetime.now(pytz.UTC)
        now_local = now_utc.astimezone(user_timezone)

        # Названия месяцев на русском
        months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        
        # Создаем календарь
        cal = calendar.monthcalendar(now_local.year, now_local.month)
        
        return {
            'current_date': now_local.strftime('%d.%m.%Y'),
            'current_time': now_local.strftime('%H:%M'),
            'timezone': user_timezone_str,
            'month': months[now_local.month],
            'year': now_local.year,
            'current_day': now_local.day,
            'calendar_weeks': cal
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_news'] = News.objects.filter(is_published=True).order_by('-created_at').first()
        context['calendar_data'] = self.generate_calendar()
        return context

class APIDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'content/api_dashboard.html'
    login_url = 'accounts:login'

    def test_func(self):
        return self.request.user.is_superuser

    def get_calendar_weeks(self):
        today = date.today()
        cal = calendar.monthcalendar(today.year, today.month)
        weeks = []
        for week in cal:
            week_days = []
            for day in week:
                if day == 0:
                    week_days.append({'day': '', 'today': False})
                else:
                    week_days.append({
                        'day': day,
                        'today': day == today.day
                    })
            weeks.append(week_days)
        return weeks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем временную зону пользователя из сессии или используем по умолчанию
        user_timezone_str = self.request.session.get('user_timezone', 'Europe/Minsk')
        try:
            user_timezone = pytz.timezone(user_timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            user_timezone = pytz.timezone('Europe/Minsk')

        # Текущее время в UTC и локальное время
        now_utc = datetime.now(pytz.UTC)
        now_local = now_utc.astimezone(user_timezone)

        context.update({
            'user_timezone': user_timezone_str,
            'utc_time': now_utc,
            'local_time': now_local,
            'current_date': now_local,
            'calendar_weeks': self.get_calendar_weeks(),
        })
        return context

class AboutView(TemplateView):
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_info'] = CompanyInfo.objects.all()
        return context

class NewsListView(ListView):
    model = News
    template_name = 'content/news_list.html'
    context_object_name = 'news_list'
    queryset = News.objects.filter(is_published=True).order_by('-created_at')

class NewsDetailView(DetailView):
    model = News
    template_name = 'content/news_detail.html'
    context_object_name = 'news'
    queryset = News.objects.filter(is_published=True)

class FAQListView(ListView):
    model = FAQ
    template_name = 'content/faq.html'
    context_object_name = 'faqs'
    queryset = FAQ.objects.filter(is_published=True)

class EmployeeListView(ListView):
    model = Employee
    template_name = 'content/contacts.html'
    context_object_name = 'employees'
    queryset = Employee.objects.all()

class PrivacyPolicyView(TemplateView):
    template_name = 'content/privacy_policy.html'

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'content/vacancy_list.html'
    context_object_name = 'vacancies'
    queryset = Vacancy.objects.filter(is_active=True)

def review_list(request):
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'content/review_list.html', {'reviews': page_obj})

@login_required
def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно создан.')
            return redirect('content:review-list')
    else:
        form = ReviewForm()
    return render(request, 'content/review_form.html', {'form': form})

@login_required
def update_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        messages.error(request, 'Вы не можете редактировать чужой отзыв.')
        return redirect('content:review-list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв успешно обновлен.')
            return redirect('content:review-list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'content/review_form.html', {'form': form, 'review': review})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        messages.error(request, 'Вы не можете удалить чужой отзыв.')
        return redirect('content:review-list')
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Ваш отзыв успешно удален.')
        return redirect('content:review-list')
    return render(request, 'content/review_confirm_delete.html', {'review': review})

class PromotionListView(ListView):
    model = Promotion
    template_name = 'content/promotions.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True).select_related('promo').order_by('-created_at')

class PrivacyView(TemplateView):
    template_name = 'content/privacy.html'
