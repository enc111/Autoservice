from django.shortcuts import render
from django.shortcuts import render_to_response, redirect,HttpResponse

def cart(request):
    args = {}
    return render_to_response('cart.html', args)