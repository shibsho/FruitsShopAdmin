from django.forms import ModelForm
from .models import Sale


class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['item', 'item_num', 'saled_at']
