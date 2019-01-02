from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
import datetime
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
    def get_recent_monthly_reports_list(cls, span):
        """
        直近数ヶ月（span）分の月間売上情報をリストで返す
        月間売上情報（monthly_sale_report）は以下の形式
        {   'year': 2018,
            'month': 12,
            'amount': 400, 
            'item_reports': [
                {'item': 'バナナ', 'item_num': 2, 'amount': 100},
                {'item': 'ぶどう', 'item_num': 3, 'amount': 300}
            ]}
        """
        today = datetime.date.today()
        monthly_sale_reports_list = list()
        for i in range(0, span):
            # 月間売上情報=monthly_sale_report(dict) を３ヶ月分作り、各々をmonthly_sale_reports_listに格納
            monthly_sale_report = dict()
            search_day = today + relativedelta(months=-i)
            year = search_day.year
            month = search_day.month
            monthly_sales = Sale.find_by_year_month(year, month)
            # 果物ごとの集計情報を作成する
            item_reports = list()
            for item in monthly_sales.values_list('item__name', flat=True).distinct():
                # 特定の果物についての売上情報を作成する
                item_report = dict()
                item_sales = monthly_sales.filter(item__name=item)
                item_report['item'] = item
                item_report['item_num'] = Sale.total_item_num_of_queryset(item_sales)
                item_report['amount'] = Sale.total_amount_of_queryset(item_sales)
                item_reports.append(item_report)
            monthly_sale_report["year"] = year
            monthly_sale_report["month"] = month
            monthly_sale_report["amount"] = Sale.total_amount_of_queryset(
            monthly_sales)
            monthly_sale_report["item_reports"] = item_reports

            # monthly_sales_report_listに格納
            monthly_sale_reports_list.append(monthly_sale_report)
        return monthly_sale_reports_list

    @classmethod
    def get_recent_daily_reports_list(cls, span):
        """
        直近数日（span）分の日間売上情報をリストで返す
        日間売上情報（daily_sale_report）は以下の形式
        {   'year': 2018,
            'month': 12,
            'day': 1,
            'amount': 400, 
            'item_reports': [
                {'item': 'バナナ', 'item_num': 2, 'amount': 100},
                {'item': 'ぶどう', 'item_num': 3, 'amount': 300}
            ]}
        """
        today = datetime.date.today()
        daily_sale_reports_list = list()
        for i in range(0, span):
            # 日間売上情報=daily_sale_report(dict) を３ヶ月分作り、各々をdaily_sale_reports_listに格納
            daily_sale_report = dict()
            search_day = today + relativedelta(days=-i)
            year = search_day.year
            month = search_day.month
            day = search_day.day
            daily_sales = Sale.find_by_year_month_day(year, month, day)
            # 果物ごとの集計情報を作成する
            item_reports = list()
            for item in daily_sales.values_list('item__name', flat=True).distinct():
                # 特定の果物についての売上情報を作成する
                item_report = dict()
                item_sales = daily_sales.filter(item__name=item)
                item_report['item'] = item
                item_report['item_num'] = Sale.total_item_num_of_queryset(item_sales)
                item_report['amount'] = Sale.total_amount_of_queryset(item_sales)
                item_reports.append(item_report)
            daily_sale_report["year"] = year
            daily_sale_report["month"] = month
            daily_sale_report["day"] = day
            daily_sale_report["amount"] = Sale.total_amount_of_queryset(daily_sales)
            daily_sale_report["item_reports"] = item_reports

            # daily_sales_report_listに格納
            daily_sale_reports_list.append(daily_sale_report)
            print(daily_sale_report)
        return daily_sale_reports_list
