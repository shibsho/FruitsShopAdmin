from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Item
from .forms import ItemForm

@login_required
def index(request):
    items = Item.get_all_objects()
    paginator = Paginator(items, 10)
    page = request.GET.get('page')
    items = paginator.get_page(page)
    return render(request, 'items/index.html',{
        'items': items,
    })


@login_required
def register(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "登録が完了しました。")
        else:
            messages.error(request, "登録に失敗しました。")
        return redirect('items:index')
    form = ItemForm
    return render(request, 'items/register.html', {
        'form': form,
    })


@login_required
def edit(request, id):
    item = Item.get_by_id_or_404(id)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
        else:
            messages.error(request, "更新に失敗しました。")
        return redirect('items:index')
    else:
        form = ItemForm(instance=item)
    return render(request, 'items/edit.html', {
        'item': item,
        'form': form,
    })


@login_required
@require_POST
def delete(request, id):
    Item.delete_by_id(id)
    return redirect('items:index')
