from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from .forms import ClientForm
from django.contrib import messages

def client_list(request):
    """Отображает список клиентов."""
    clients = Client.objects.all()
    context = {'clients': clients}
    return render(request, 'clients/client_list.html', context)

def client_detail(request, id):
    """Отображает детали клиента."""
    client = get_object_or_404(Client, id=id)
    context = {'client': client}
    return render(request, 'clients/client_detail.html', context)

def client_create(request):
    """Создает нового клиента."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент успешно добавлен.')
            return redirect('clients:client_list')
    else:
        form = ClientForm()
    context = {'form': form}
    return render(request, 'clients/client_form.html', context)

def client_update(request, id):
    """Обновляет информацию о клиенте."""
    client = get_object_or_404(Client, id=id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о клиенте успешно обновлена.')
            return redirect('clients:client_detail', id=client.id)
    else:
        form = ClientForm(instance=client)
    context = {'form': form, 'client': client}
    return render(request, 'clients/client_form.html', context)

def client_delete(request, id):
    """Удаляет клиента."""
    client = get_object_or_404(Client, id=id)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Клиент успешно удален.')
        return redirect('clients:client_list')
    context = {'client': client}
    return render(request, 'clients/client_confirm_delete.html', context)