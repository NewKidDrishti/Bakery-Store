# BAKERY/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem
from django.db import transaction
from django.http import JsonResponse

# The view to display your dynamic product catalog
def product_list(request):
    products = Product.objects.all()
    print(f"Products fetched from DB: {products}")
    context = {
        'products': products
    }
    return render(request, 'product_list.html', context)

# Your landing page view
def WEbpage(request):
    return render(request, 'WEbpage.html')

# Helper function to get or create a cart for the current user/session
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

# The view to add products to the cart with quantity and stock checks
@login_required
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': "Invalid quantity."})

    if quantity <= 0:
        return JsonResponse({'success': False, 'message': "Quantity must be at least 1."})

    with transaction.atomic():
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock < quantity:
            return JsonResponse({'success': False, 'message': f"Sorry, we only have {product.stock} {product.name}(s) left in stock."})

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created and (cart_item.quantity + quantity > product.stock):
             return JsonResponse({'success': False, 'message': f"Adding this many would exceed available stock."})

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        
        product.stock -= quantity
        product.save()

    # Return a JSON response instead of a redirect
    return JsonResponse({
        'success': True,
        'message': f"Added {quantity} {product.name}(s) to your cart.",
        'new_stock': product.stock
    })
# The view to display the contents of the cart
def view_cart(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    total_price = sum(item.get_total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

# The view to remove an item from the cart
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.cart == get_or_create_cart(request):
        cart_item.delete()
    return redirect('view_cart')


# ---- PLACEHOLDER VIEWS FOR NAVIGATION LINKS ----
# These are simple views to prevent "Not Found" errors for your header links
def profile(request):
    return render(request, 'profile.html') # You will need to create this template

def logout_view(request):
    # This is a placeholder. You will need to add Django's logout logic here.
    return redirect('WEbpage') # Or wherever you want to redirect after logout

def orders(request):
    # This is a placeholder for a future orders page.
    return render(request, 'orders.html') # You will need to create this template