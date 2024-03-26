from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request,'marketplace/listings.html', context=context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    # categories = Category.objects.filter(vendor=vendor)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems', #related name in Menu fooditems.model in categories
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context=context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # if request.is_ajax(): #Depricated
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    #Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increase the cart quantity', 'cart_counter': get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem = fooditem, quantity = 1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
        return JsonResponse({'status': 'Success', 'message': 'User is logged in'})
    # return HttpResponse(food_id)
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_id):
    # return HttpResponse(food_id)
    if request.user.is_authenticated:
        # if request.is_ajax(): #Depricated
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity >= 1 :
                    #decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                        return JsonResponse({'status': 'Success', 'message': 'Decrease the cart quantity', 'cart_counter': get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                    else:
                        chkCart.delete()
                        return JsonResponse({'status': 'Success', 'message': 'Deleted the cart', 'cart_counter': get_cart_counter(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have item in your cart'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
        return JsonResponse({'status': 'Success', 'message': 'User is logged in'})
    # return HttpResponse(food_id)
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context=context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #Check if cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart Item has been deleted', 'cart_counter': get_cart_counter(request), 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})