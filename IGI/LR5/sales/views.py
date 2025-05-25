from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from .models import Sale
from shop.models import Product
from clients.models import Client
from .forms import SaleForm
from django.contrib import messages
from django.db import transaction

def sale_list(request):
    """Отображает список продаж."""
    sales = Sale.objects.all()
    context = {'sales': sales}
    return render(request, 'sales/sale_list.html', context)

def sale_detail(request, id):
    """Отображает детали продажи."""
    sale = get_object_or_404(Sale, id=id)
    context = {'sale': sale}
    return render(request, 'sales/sale_detail.html', context)

def sale_create(request):
    """Создает новую продажу."""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продажа успешно добавлена.')
            return redirect('sales:sale_list')
    else:
        form = SaleForm()
    context = {'form': form}
    return render(request, 'sales/sale_form.html', context)

def sale_update(request, id):
    """Обновляет информацию о продаже."""
    sale = get_object_or_404(Sale, id=id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о продаже успешно обновлена.')
            return redirect('sales:sale_detail', id=sale.id)
    else:
        form = SaleForm(instance=sale)
    context = {'form': form, 'sale': sale}
    return render(request, 'sales/sale_form.html', context)

def sale_delete(request, id):
    """Удаляет продажу."""
    sale = get_object_or_404(Sale, id=id)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Продажа успешно удалена.')
        return redirect('sales:sale_list')
    context = {'sale': sale}
    return render(request, 'sales/sale_confirm_delete.html', context)