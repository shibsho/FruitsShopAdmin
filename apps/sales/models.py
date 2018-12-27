from django.db import models
from django.utils import timezone
from apps.items.models import Item


class Sale(models.Model):
    item = models.ForeignKey(Item, verbose_name="果物", on_delete=models.CASCADE)
    number = models.PositiveIntegerField("個数")
    saled_at = models.DateTimeField("販売日時")

    @property
    def get_amount(self):
        return self.item.price * self.number

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all().order_by('-saled_at')
