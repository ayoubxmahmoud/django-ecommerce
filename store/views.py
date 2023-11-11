import json
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.decorators import login_required
from .forms import CustomerCreationForm, CustomerUpdateForm


from django.contrib import messages


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('store')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, "User does not exist")

        customer = authenticate(request, email=email, password=password)

        if customer is not None:
            login(request, customer)
            return redirect('store')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'store/login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('login')

def registerPage(request):
    form = CustomerCreationForm()

    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            # Save the form to get the Customer object
            customer = form.save(commit=False)
            customer.username = customer.username.lower()
            customer.save()
            login(request, customer)
            return redirect('store')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'store/login_register.html', {'form': form})


def userProfile(request, pk):
    user = Customer.objects.get(id=pk)

    context = {'user' : user}
    return render(request, 'store/profile.html', context)

def updateUser(request):
    user = request.user
    form = CustomerUpdateForm(instance=user)

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)
        
    return render(request, 'store/update-user.html', {'form': form})

# Define a view function called 'store' that takes a 'request' object a parameter
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    # Create an empty context dictionary to pass data to the template
    context = {'products' : products, 'cartItems' :cartItems}
    # Render the 'store.html' template with the provided context
    # and return the rendered HTML as response to the client
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
        
    context = {'items' : items, 'order' : order, 'cartItems' :cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items' : items, 'order' : order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse('Item was added', safe=False)

def proccessOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
        )

    return JsonResponse('Payment complete!', safe=False)


def displayProduct(request, product_id):
    product = Product.objects.get(id=product_id)
    product_desc_list = product.desc.split('\n')
    data = cartData(request)
    cartItems = data['cartItems']

    context = {'product': product, 'product_desc_list': product_desc_list, 'cartItems' : cartItems}
    return render(request, 'store/show.html',  context)