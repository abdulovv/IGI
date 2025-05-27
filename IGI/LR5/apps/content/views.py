from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import News, CompanyInfo, FAQ, Review, Vacancy, Promotion, Employee
from .forms import ReviewForm

class HomeView(TemplateView):
    template_name = 'content/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_news'] = News.objects.filter(is_published=True).order_by('-created_at').first()
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

class PromotionListView(ListView):
    model = Promotion
    template_name = 'content/promotions.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True).select_related('promo').order_by('-created_at')

class PrivacyView(TemplateView):
    template_name = 'content/privacy.html'
