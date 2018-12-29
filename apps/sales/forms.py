from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
from .models import Sale



class SaleForm(ModelForm):
	# saled_at = forms.DateTimeField(
	# 		label = "売上",
    #         widget=forms.widgets.DateTimeInput(
    #         	attrs={'type': 'datetime-local',
	# 					  })
    #     )


	# def __init__(self, *args, **kwargs):
	# 	super(SaleForm, self).__init__(*args, **kwargs)
	# 	self.fields['saled_at'].widget = widgets.AdminSplitDateTime()

	class Meta:
		model = Sale
		fields = ['item', 'item_num', 'saled_at']


	
		
"""
class ShowForm(ModelForm):
    class Meta:
        model = Show

    def __init__(self, *args, **kwargs):
        super(ShowForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].widget = widgets.AdminSplitDateTime()
        self.fields['sale_end_time'].widget = widgets.AdminSplitDateTime()
"""
