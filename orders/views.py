from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order
import simplejson as json
from .models import Order, OrderedFood
from .utils import generate_order_number 
from django.contrib import messages

# Create your views here.


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.city = form.cleaned_data['city']
            order.eir_code = form.cleaned_data['eir_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            order.is_ordered = True
            order.save()
            
            cart_items = Cart.objects.filter(user=request.user)
            for item in cart_items:
                ordered_food = OrderedFood()
                ordered_food.order = order
                ordered_food.user = request.user
                ordered_food.fooditem = item.fooditem
                ordered_food.quantity = item.quantity
                ordered_food.price = item.fooditem.price
                ordered_food.amount = item.fooditem.price * item.quantity # total amount
                ordered_food.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            messages.success(request, 'Congratulation! Your Order is placed...')
            return render(request, 'home.html', context)
            #return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)


    return render(request, 'orders/place_order.html')

