from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
from .models import Sale



class SaleForm(ModelForm):
	class Meta:
		model = Sale
		fields = ['item', 'item_num', 'saled_at']
