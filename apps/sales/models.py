from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from apps.items.models import Item


class Sale(models.Model):
    item = models.ForeignKey(Item, verbose_name="果物", on_delete=models.CASCADE)
    number = models.PositiveIntegerField("個数")
    amount = models.PositiveIntegerField("売上", editable=False)
    saled_at = models.DateTimeField("販売日時")

    def save(self, *args, **kwargs):
        if kwargs.get('calc_amount') == True:
            self.amount = self.item.price * self.number
            kwargs = dict()
        super().save(*args, **kwargs)

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all().order_by('-saled_at')

    @classmethod
    def get_by_id_or_404(cls, id):
        return get_object_or_404(cls, id=id)

    @classmethod
    def delete_by_id(cls, id):
        cls.objects.get(id=id).delete()

    @classmethod
    def get_entire_period_amount(cls):
        return cls.objects.all().aggregate(Sum('amount'))['amount__sum']
