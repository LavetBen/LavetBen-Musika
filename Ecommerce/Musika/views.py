from django.shortcuts import render
from .models import Product,Order,OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User


def store(request):
    return render(request,'store.html')

def home(request):
    products = Product.objects.all()
    return render(request, 'store.html', {'products': products})

@login_required
def place_order(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Order.objects.create(user=request.user, product=product)
    return redirect('home')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        messages.success(request, "Registration successful")
        return redirect('home')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity

        request.session['cart'] = cart
        messages.success(request, f'Added {quantity} x {product.name} to your cart.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('home')

@login_required(login_url='login')
def view_cart(request):
    cart = request.session.get('cart', {})  
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    
    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='login')
def quick_checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.info(request, "Your cart is empty.")
            return redirect('home')

        address = request.POST.get('address', 'Not provided')
        city = request.POST.get('city', 'Unknown')
        postal_code = request.POST.get('postal_code', '0000')

        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            address=address,
            city=city,
            postal_code=postal_code
        )

        for product in products:
            quantity = cart.get(str(product.id), 0)
            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

        request.session['cart'] = {}
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation', order_id=order.id)

    return redirect('home')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  


@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product = get_object_or_404(Product, id=product_id)

        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            messages.success(request, f"Removed {product.name} from your cart.")
        else:
            messages.error(request, "Product not in cart.")

    return redirect('view_cart')