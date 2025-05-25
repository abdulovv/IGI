from django.shortcuts import render
from .models import CompanyInfo, NewsArticle

def home(request):
    """Отображает главную страницу."""
    latest_article = NewsArticle.objects.order_by('-publication_date').first()  #  Последняя статья
    context = {'latest_article': latest_article}
    return render(request, 'core/home.html', context)

def about(request):
    """Отображает страницу "О компании"."""
    company_info = CompanyInfo.objects.first()  #  Предполагаем, что запись одна
    context = {'company_info': company_info}
    return render(request, 'core/about.html', context)

def news_list(request):
    """Отображает список новостей."""
    articles = NewsArticle.objects.order_by('-publication_date')
    context = {'articles': articles}
    return render(request, 'core/news_list.html', context)

def news_detail(request, id):
    """Отображает детали новости."""
    article = NewsArticle.objects.get(id=id)
    context = {'article': article}
    return render(request, 'core/news_detail.html', context)