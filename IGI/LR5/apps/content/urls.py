from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.EmployeeListView.as_view(), name='contacts'),
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('news/', views.NewsListView.as_view(), name='news-list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news-detail'),
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-edit'),
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('vacancies/', views.VacancyListView.as_view(), name='vacancies'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('api-dashboard/', views.APIDashboardView.as_view(), name='api-dashboard'),
]
