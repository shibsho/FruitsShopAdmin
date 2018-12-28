from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from io import TextIOWrapper
import csv
import datetime
from .models import Sale
from apps.items.models import Item
from .forms import SaleForm

@login_required
def index(request):
    sales = Sale.get_all_objects()
    return render(request, 'sales/index.html', {
        'sales': sales,
    })


@login_required
def register(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.save(calc_amount=True)
            messages.success(request, "登録が完了しました。")
        else:
            messages.error(request, "登録に失敗しました。")
        return redirect('sales:index')
    form = SaleForm
    return render(request, 'sales/register.html', {
        'form': form,
    })


@login_required
def edit(request, id):
    sale = Sale.get_by_id_or_404(id)
    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
        else:
            messages.error(request, "更新に失敗しました。")
        return redirect('sales:index')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales/edit.html', {
        'sale': sale,
        'form': form,
    })


@login_required
@require_POST
def delete(request, id):
    Sale.delete_by_id(id)
    return redirect('sales:index')


@login_required
@require_POST
def csv_upload(request):
    f = request.FILES['file']
    if f.content_type == "text/csv":
        csv_file = TextIOWrapper(f.file, encoding='utf-8')
        data = csv.reader(csv_file)

        def validate_data(number, amount, saled_at):
            try:
                int(number)
                int(amount)
                datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M")
            except:
                return False
            return True

        for row in data:
            item = Item.get_by_name_or_none(row[0])
            number = row[1]
            amount = row[2]
            saled_at = row[3]
            if item is not None and validate_data(number, amount, saled_at):
                Sale.objects.create(
                    item=item,
                    number=int(row[1]),
                    amount = int(row[2]),
                    saled_at=datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M")
                    )
        return redirect('sales:index')
    # csv以外がアップロードされた場合
    else:
        messages.error(request, "csvファイルをアップロードして下さい")
        return redirect('sales:index')


@login_required
def statics(request):
    entire_period_amount = Sale.get_entire_period_amount()
    return render(request, 'sales/statics.html',{
        'entire_period_amount': entire_period_amount,
    })
