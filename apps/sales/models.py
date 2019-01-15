import datetime
from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Sum
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
        return (cls.objects.filter(saled_at__year=year)
                           .filter(saled_at__month=month))

    @classmethod
    def find_by_year_month_day(cls, year, month, day):
        # 指定された年月日から、全ての販売情報を取得
        return (cls.objects.filter(saled_at__year=year)
                           .filter(saled_at__month=month)
                           .filter(saled_at__day=day))

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
