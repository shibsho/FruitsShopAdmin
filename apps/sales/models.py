from django.utils.timezone import localtime
import datetime
from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from collections import OrderedDict, namedtuple
from apps.items.models import Item


class Sale(models.Model):
    item = models.ForeignKey(Item, verbose_name="果物", on_delete=models.CASCADE)
    item_num = models.PositiveIntegerField("個数")
    amount = models.PositiveIntegerField("売上", blank=True)
    saled_at = models.DateTimeField("販売日時")

    def save(self, *args, **kwargs):
        # amountフィールドが空欄の時(ページからの新規登録)は、単価*個数を売上とする
        if self.amount is None:
            self.amount = self.item.price * self.item_num
        super().save(*args, **kwargs)

    @classmethod
    def get_all_object(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id_or_404(cls, id):
        return get_object_or_404(cls, id=id)

    @classmethod
    def delete_by_id(cls, id):
        cls.objects.get(id=id).delete()

    @classmethod
    def find_by_year_month(cls, year, month):
        # 指定された年月から、全ての販売情報を取得
        return cls.objects.filter(saled_at__year=year).filter(saled_at__month=month)

    @classmethod
    def find_by_year_month_day(cls, year, month, day):
        # 指定された年月日から、全ての販売情報を取得
        return cls.objects.filter(saled_at__year=year).filter(saled_at__month=month).filter(saled_at__day=day)

    @staticmethod
    def total_amount_of_queryset(queryset):
        # 販売情報クエリセットの売上総額を取得
        if queryset.exists():
            return queryset.aggregate(Sum('amount'))['amount__sum']
        return 0
    
    @staticmethod
    def total_item_num_of_queryset(queryset):
        # 販売情報クエリセットの果物総個数を取得
        if queryset.exists():
            return queryset.aggregate(Sum('item_num'))['item_num__sum']
        return 0
    
    @classmethod
    def get_entire_amount(cls):
        sales = cls.objects.all()
        amount = 0
        for sale in sales:
            amount += sale.amount
        return amount
    
    @classmethod
    def get_recent_monthly_reports(cls, span):
        """
        直近数ヶ月（span）分の月間売上情報をdictで返す
        月間売上情報dict（monthly_sale_reports） は以下の形式
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
        today = datetime.date.today()
        monthly_sale_reports = OrderedDict()
        YearMonth = namedtuple('YearMonth', ('year', 'month'))
        for i in range(0, span):
            day = today + relativedelta(months=-i)
            year_month = YearMonth(
                year=day.year,
                month=day.month
                )
            monthly_sale_reports[year_month] = {
                'amount': 0,
                'item_reports': {}
            }

        sales = Sale.objects.all()
        for sale in sales:
            # saleの販売日をタプルに変換 => (2018,12)
            saled_at_date = localtime(sale.saled_at).date()
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
            if sale.item.name in monthly_sale_reports[saled_at]['item_reports']:
                monthly_sale_reports[saled_at]['item_reports'][sale.item.name]['item_num'] += sale.item_num
                monthly_sale_reports[saled_at]['item_reports'][sale.item.name]['amount'] += sale.amount
            # item_reportsにsaleの果物がキーとして存在しないとき
            else:
                monthly_sale_reports[saled_at]['item_reports'][sale.item.name] = {
                    'item_num': sale.item_num,
                    'amount': sale.amount
                }
        return monthly_sale_reports

    @classmethod
    def get_recent_daily_reports(cls, span):
        """
        直近数日（span）分の日間売上情報をdictで返す
        月間売上情報dict（daily_sale_reports） は以下の形式
        {
            (2018,12,31):{
                'amount': 400, 
                'item_reports': {
                    'バナナ': {'item_num': 2, 'amount': 100},
                    'ぶどう': {'item_num': 3, 'amount': 300}
                }
            },
            (2018,12,30):{
                'amount': 400, 
                'item_reports': {
                    'バナナ': {'item_num': 2, 'amount': 100},
                    'ぶどう': {'item_num': 3, 'amount': 300}
                }
            }
        }
        """

        # 対象日のタプル(yyyy,mm,dd)を作り、daily_sale_reportsのキーとして設定
        today = datetime.date.today()
        daily_sale_reports = OrderedDict()
        YearMonthDay = namedtuple('YearMonthDay', ('year', 'month', 'day'))
        for i in range(0, span):
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
        
        sales = Sale.objects.all()
        for sale in sales:
            # saleの販売日をタプルに変換 => (2018,12,31)
            saled_at_date = localtime(sale.saled_at).date()
            saled_at = YearMonthDay(
                year = saled_at_date.year,
                month = saled_at_date.month,
                day = saled_at_date.day
                )

            # 対象期間外のsaleであれば何も処理しない
            if saled_at not in daily_sale_reports.keys():
                continue

            # 対象日の売上総額を加算
            daily_sale_reports[saled_at]['amount'] += sale.amount
            # item_reportsにsaleの果物がキーとして存在するとき
            if sale.item.name in daily_sale_reports[saled_at]['item_reports']:
                daily_sale_reports[saled_at]['item_reports'][sale.item.name]['item_num'] += sale.item_num
                daily_sale_reports[saled_at]['item_reports'][sale.item.name]['amount'] += sale.amount
            # item_reportsにsaleの果物がキーとして存在しないとき
            else:
                daily_sale_reports[saled_at]['item_reports'][sale.item.name] = {
                    'item_num': sale.item_num,
                    'amount': sale.amount
                }
        return daily_sale_reports
