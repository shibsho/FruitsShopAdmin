from django.db import models
from django.shortcuts import get_object_or_404


class Item(models.Model):
    name = models.CharField("名称", max_length=190, unique=True)
    price = models.PositiveIntegerField("単価")
    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_objects(cls):
        return cls.objects.all().order_by('-updated_at')

    @classmethod
    def get_by_id_or_404(cls, id):
        return get_object_or_404(cls, id=id)

    @classmethod
    def get_by_name_or_none(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None

    @classmethod
    def delete_by_id(cls, id):
        cls.objects.get(id=id).delete()
