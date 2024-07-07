from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .cart import Cart
from ecommerceapp.models import Product
from django.http import JsonResponse
from django.contrib import messages
from PayTm.models import ShippingAddress
from django.core.paginator import Paginator

def cart_summary(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

# Begin - Calculating Cart Product and quantity wise totol price
    prod_totals = {}
    prod_val = cart.get_prods_dict()
    prod_qty = cart.get_quants_dict()

    for i in range(len(prod_val)):
            for key, value in prod_qty.items():
                # Convert key string into into so we can do math
                key = int(key)
                if key == prod_val[i]['product_id']:
                    if prod_val[i]['is_sale']:
                        price = prod_val[i]['sale_price']
                    else:
                        price = prod_val[i]['price']
                    prod_totals[str(key)] = float(value * price)

        # End - Calculating Cart Product and quantity wise totol price
    if request.user.is_authenticated :
            current_user = request.user.id
            shipment = ShippingAddress.objects.filter(user__id=request.user.id).order_by('shipping_id').all()

            paginator = Paginator(shipment, 1)  # Show 1 Shipping Address per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, "cart_summary.html",
                          {"cart_products": cart_products, "quantities": quantities, "totals": totals,
                           "prod_totals": prod_totals, 'page_obj': page_obj})
    else :
            page_obj ='No'
            return render(request, "cart_summary.html",
                  {"cart_products": cart_products, "quantities": quantities, "totals": totals, "prod_totals":prod_totals, 'page_obj': page_obj })


def cart_add(request):
    # Get the cart
    cart = Cart(request)
    # test for POST
    print(' Cart : '+str(cart))
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # lookup product in DB
        product = get_object_or_404(Product, product_id=product_id)

        # Save to session
        cart.add(product=product, quantity=product_qty)

        # Get Cart Quantity
        cart_quantity = cart.__len__()

        # Return resonse
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart..."))
        return response

def cart_delete(request):
    # Get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        # Call delete Function in Cart
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        # return redirect('cart_summary')
        messages.success(request, ("Product Deleted From Shopping Cart..."))
        return response


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})
        # return redirect('cart_summary')
        messages.success(request, ("Your Cart Has Been Updated..."))
        return response
