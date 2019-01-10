from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from io import TextIOWrapper
import csv, datetime
from dateutil.relativedelta import relativedelta
from .models import Sale
from apps.items.models import Item
from .forms import SaleForm
from django.db.models import Sum

@login_required
def index(request):
    sales = Sale.get_all_object().order_by('-saled_at')
    paginator = Paginator(sales, 10)
    page = request.GET.get('page')
    sales = paginator.get_page(page)
    return render(request, 'sales/index.html', {
        'sales': sales,
    })


@login_required
def register(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
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

        def validate_data(item_num, amount, saled_at):
            try:
                int(item_num)
                int(amount)
                datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M")
            except:
                return False
            return True

        for row in data:
            item = Item.get_by_name_or_none(row[0])
            item_num = row[1]
            amount = row[2]
            saled_at = row[3]
            if item is not None and validate_data(item_num, amount, saled_at):
                Sale.objects.create(
                    item=item,
                    item_num=int(row[1]),
                    amount = int(row[2]),
                    saled_at=datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M")
                    )
        return redirect('sales:index')
    # csv以外がアップロードされた場合
    else:
        messages.error(request, "csvファイルをアップロードして下さい")
        return redirect('sales:index')


@login_required
def statistics(request):
    # 全期間
    entire_sales_amount = Sale.get_entire_amount()
    # 過去３ヶ月
    monthly_sale_reports = Sale.get_recent_monthly_reports(3)
    # 過去３日
    daily_sale_reports = Sale.get_recent_daily_reports(3)

    return render(request, 'sales/statistics.html',{
        'entire_sales_amount': entire_sales_amount,
        'monthly_sale_reports': monthly_sale_reports,
        'daily_sale_reports': daily_sale_reports,
    })
