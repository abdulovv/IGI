from django.shortcuts import render, get_object_or_404, redirect
from .models import Supplier
from .forms import SupplierForm  #  Создадим этот файл позже
from django.contrib import messages

def supplier_list(request):
    """Отображает список поставщиков."""
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'suppliers/supplier_list.html', context)

def supplier_detail(request, id):
    """Отображает детали поставщика."""
    supplier = get_object_or_404(Supplier, id=id)
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_detail.html', context)

def supplier_create(request):
    """Создает нового поставщика."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Поставщик успешно добавлен.')
            return redirect('suppliers:supplier_list')
    else:
        form = SupplierForm()
    context = {'form': form}
    return render(request, 'suppliers/supplier_form.html', context)

def supplier_update(request, id):
    """Обновляет информацию о поставщике."""
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о поставщике успешно обновлена.')
            return redirect('suppliers:supplier_detail', id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)
    context = {'form': form, 'supplier': supplier}
    return render(request, 'suppliers/supplier_form.html', context)

def supplier_delete(request, id):
    """Удаляет поставщика."""
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Поставщик успешно удален.')
        return redirect('suppliers:supplier_list')
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_confirm_delete.html', context)