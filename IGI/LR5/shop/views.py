from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request, category_slug=None):
    """
    Отображает список товаров.
    Если указан category_slug, отображает товары только этой категории.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)  #  Предполагаем, что у Category есть поле slug
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, id):
    """
    Отображает детали конкретного товара.
    """
    product = get_object_or_404(Product, id=id)
    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)