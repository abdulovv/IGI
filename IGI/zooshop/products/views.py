from django.shortcuts import render, get_object_or_404
from .models import Supplier, Product, Purchase, PriceChange, Category


def index(request):
    products = Product.objects.all()[:6]  # Показываем только 6 последних продуктов на главной
    return render(
        request,
        'products/product_list.html',
        {'product_list': products}
    )


def catalog_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    current_category = None

    query = request.GET.get('product-name', '')
    articul_search = request.GET.get('articul-search', False)

    if query:
        if articul_search:
            products = products.filter(article_number__icontains=query)
        else:
            products = products.filter(name__icontains=query)

    sorting = request.GET.get('sorting', 'name')
    if sorting == 'price_asc':
        products = products.order_by('price')
    elif sorting == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    return render(
        request,
        'products/product_list.html',
        {
            'product_list': products,
            'categories': categories,
            'current_category': current_category,
            'query': query,
            'sorting': sorting
        }
    )


def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()

    return render(
        request,
        'products/product_list.html',
        {
            'product_list': products,
            'categories': categories,
            'current_category': category,
            'category': category
        }
    )
