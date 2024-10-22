# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, TemplateDoesNotExist
from django.urls import reverse
from django.shortcuts import render


@login_required
def index(request):
    return render(request, 'home/index.html')


@login_required
def pages(request, template_name):
    context = {}
    try:
        load_template = template_name
        if template_name == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template(f'home/{load_template}.html')
        return render(request, f'home/{load_template}.html', context)
    except TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return render(request, 'home/page-404.html', context, status=404)
    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return render(request, 'home/page-500.html', context, status=500)


@login_required
def profile(request):
    return render(request, 'home/profile.html')


@login_required
def map_view(request):
    return render(request, 'home/map.html')


def home(request):
    return render(request, 'home/index.html')
