import csv
import datetime
from collections import OrderedDict, namedtuple
from io import TextIOWrapper

from apps.items.models import Item
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST

from .forms import SaleForm
from .models import Sale


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
            except ValueError:
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
                    amount=int(row[2]),
                    saled_at=datetime.datetime.strptime(
                        row[3], "%Y-%m-%d %H:%M")
                )
        return redirect('sales:index')
    # csv以外がアップロードされた場合
    else:
        messages.error(request, "csvファイルをアップロードして下さい")
        return redirect('sales:index')


@login_required
def statistics(request):
    today = datetime.date.today()
    sales = Sale.objects.all()
    entire_sales_amount = 0

    """
    直近3ヶ月分の月間売上情報dict（monthly_sale_reports）と
    直近3日分の日間売上情報dict（daily_sale_reports） を作る
    {
        (2018,12):{
            'amount': 400,
            'item_reports': {
                'バナナ': {'item_num': 2, 'amount': 100},
                'ぶどう': {'item_num': 3, 'amount': 300}
            }
        },
        (2018,11):{
            'amount': 400,
            'item_reports': {
                'バナナ': {'item_num': 2, 'amount': 100},
                'ぶどう': {'item_num': 3, 'amount': 300}
            }
        }
    }
    """
    # 対象月のタプル(yyyy,mm)を作り、monthly_sale_reportsのキーとして設定
    monthly_sale_reports = OrderedDict()
    YearMonth = namedtuple('YearMonth', ('year', 'month'))
    # 対象日のタプル(yyyy,mm,dd)を作り、daily_sale_reportsのキーとして設定
    daily_sale_reports = OrderedDict()
    YearMonthDay = namedtuple('YearMonthDay', ('year', 'month', 'day'))
    for i in range(3):
        # 月
        day = today + relativedelta(months=-i)
        year_month = YearMonth(
            year=day.year,
            month=day.month
        )
        monthly_sale_reports[year_month] = {
            'amount': 0,
            'item_reports': {}
        }

        # 日
        day = today + relativedelta(days=-i)
        year_month_day = YearMonthDay(
            year=day.year,
            month=day.month,
            day=day.day
        )
        daily_sale_reports[year_month_day] = {
            'amount': 0,
            'item_reports': {}
        }

    # 集計
    for sale in sales:
        saled_at_date = localtime(sale.saled_at).date()

        """ 全期間 """
        entire_sales_amount += sale.amount

        """ 過去3ヶ月間 """
        # saleの販売日をタプルに変換 => (2018,12)
        saled_at = YearMonth(
            year=saled_at_date.year,
            month=saled_at_date.month,
        )

        # 対象期間外のsaleであれば何も処理しない
        if saled_at not in monthly_sale_reports.keys():
            continue

        # 対象月の売上総額を加算
        monthly_sale_reports[saled_at]['amount'] += sale.amount
        # item_reportsにsaleの果物がキーとして存在するとき
        if (sale.item.name in
                monthly_sale_reports[saled_at]['item_reports']):
            (monthly_sale_reports[saled_at]['item_reports']
             [sale.item.name]['item_num']) += sale.item_num
            (monthly_sale_reports[saled_at]['item_reports']
             [sale.item.name]['amount']) += sale.amount
        # item_reportsにsaleの果物がキーとして存在しないとき
        else:
            (monthly_sale_reports[saled_at]
             ['item_reports'][sale.item.name]) = {
                'item_num': sale.item_num,
                'amount': sale.amount
            }

        """ 過去3日間 """
        # saleの販売日をタプルに変換 => (2018,12,31)
        saled_at = YearMonthDay(
            year=saled_at_date.year,
            month=saled_at_date.month,
            day=saled_at_date.day
        )

        # 対象期間外のsaleであれば何も処理しない
        if saled_at not in daily_sale_reports.keys():
            continue

        # 対象日の売上総額を加算
        daily_sale_reports[saled_at]['amount'] += sale.amount
        # item_reportsにsaleの果物がキーとして存在するとき
        if (sale.item.name in
                daily_sale_reports[saled_at]['item_reports']):
            (daily_sale_reports[saled_at]['item_reports']
             [sale.item.name]['item_num']) += sale.item_num
            (daily_sale_reports[saled_at]['item_reports']
             [sale.item.name]['amount']) += sale.amount
        # item_reportsにsaleの果物がキーとして存在しないとき
        else:
            (daily_sale_reports[saled_at]
             ['item_reports'][sale.item.name]) = {
                'item_num': sale.item_num,
                'amount': sale.amount
            }

    return render(request, 'sales/statistics.html', {
        'entire_sales_amount': entire_sales_amount,
        'monthly_sale_reports': monthly_sale_reports,
        'daily_sale_reports': daily_sale_reports,
    })
