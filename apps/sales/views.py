from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Sale

@login_required
def index(request):
    sales = Sale.get_all_objects()
    return render(request, 'sales/index.html', {
        'sales': sales,
    })