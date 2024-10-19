# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


@login_required
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required
def pages(request):
    context = {}

    def custom_page_not_found_view(request, exception):
        return render(request, "home/page-404.html", status=404)

    def custom_error_view(request):
        return render(request, "home/page-500.html", status=500)

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
from django.shortcuts import render

@login_required
def profile(request):
    context = {'segment': 'profile'}
    return render(request, 'home/profile.html', context)

@login_required
def map_view(request):
    context = {'segment': 'map'}
    return render(request, 'home/map.html', context)

def home(request):
    return render(request, 'home/index.html')
