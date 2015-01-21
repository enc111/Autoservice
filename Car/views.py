from django.shortcuts import render
from django.template import RequestContext
from Car.models import Car, Comments
from django.shortcuts import render_to_response, redirect,HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.models import User
# Create your views here.
from .forms import CommentForm
from django.contrib import auth


def car_all(request):
    return render_to_response(
        'car_all.html',
        {'form': Car.objects.all(), 'username': auth.get_user(request).username},
        context_instance=RequestContext(request)
    )


def car(request, car_id=1):
    comments_form = CommentForm
    args = {}
    args.update(csrf(request))
    args['car'] = Car.objects.get(id=car_id)
    args['comments'] = Comments.objects.filter(comments_car_id=car_id)
    args['form'] = comments_form
    args['username'] = auth.get_user(request).username
    return render_to_response('car.html', args, context_instance=RequestContext(request))


def shop_inf(request):
    comments_form = CommentForm
    args = {}
    return render_to_response('shop_inf.html', args)


def add_comments(request, car_id):
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.comments_car = Car.objects.get(id=car_id)
            form.save()
    return redirect('/cars/get/%s/' % car_id)

def load_cart(request):

    if request.is_ajax():
        if request.session.get('cart_price') is not None:
            cart_price = request.session.get('cart_price')
        else:
            cart_price = 0
        message = cart_price
    else:
        message = 'error'
    return HttpResponse(message)

def add_car(request):

    if request.is_ajax():
        car_id = request.GET.get('id')
        if request.session.get(car_id) is not None:
            request.session[car_id] += 1
        else:
            request.session[car_id] = 1

        car = Car.objects.get(id=car_id)
        if request.session.get('cart_price') is not None:
            request.session['cart_price'] += car.price
        else:
            request.session['cart_price'] = car.price

        message = 'ok'
    else:
        message = 'error'
    return HttpResponse(message)