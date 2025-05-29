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

class HomeView(TemplateView):
    template_name = 'content/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_news'] = News.objects.filter(is_published=True).order_by('-created_at').first()
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

class ReviewListView(ListView):
    model = Review
    template_name = 'content/review_list.html'
    context_object_name = 'reviews'
    queryset = Review.objects.filter(is_published=True).order_by('-created_at')
    paginate_by = 5

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'content/review_form.html'
    success_url = reverse_lazy('content:review-list')
    login_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'content/review_form.html'
    success_url = reverse_lazy('content:review-list')

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваш отзыв успешно обновлен.')
        return super().form_valid(form)

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'content/review_confirm_delete.html'
    success_url = reverse_lazy('content:review-list')

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ваш отзыв успешно удален.')
        return super().delete(request, *args, **kwargs)

class PromotionListView(ListView):
    model = Promotion
    template_name = 'content/promotions.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True).select_related('promo').order_by('-created_at')

class PrivacyView(TemplateView):
    template_name = 'content/privacy.html'
