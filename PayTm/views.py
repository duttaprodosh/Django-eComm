from django.shortcuts import render, redirect
from django.contrib import messages
from ecommerceapp.models import Profile, Orders, OrderUpdate, OrderItem
from PayTm.models import ShippingAddress
from PayTm.forms import ShippingForm
from cart.cart import Cart
from cartauth.utils import send_mail_to_client
from datetime import datetime
from django.db.models import Q, F
from django.template.loader import get_template
from django.views.decorators.csrf import  csrf_exempt
import random
from PayTm import Checksum, keys



# Create your views here.
def checkout(request):
    if request.POST:
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


        # Get Shipping Info from the last HTML page
        full_name = request.POST.get('name')
        shipping_id = request.POST.get('shipping_id')
        shipping_address1 = request.POST.get('address1')
        shipping_address2 = request.POST.get('address2')
        city     = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        country = request.POST.get('country')
        # Create Combined Shipping Address
        shipping_address = f"{shipping_address1}\n{shipping_address2}\n{city}\n{state}\n{zip_code}\n"

        #if request.user.is_authenticated:
        #    current_user = request.user.id
        #    ship_address = ShippingAddress.objects.get(user__id=current_user)

        #   if ship_address :
        #       ship_address.shipping_full_name=full_name
        #       ship_address.shipping_email=email
        #       ship_address.shipping_phone=phone
        #       address1 = ship_address.shipping_address1
        #        address2 = ship_address.shipping_address2

        #    ship_address.shipping_city=my_shipping['shipping_city']
        #    ship_address.shipping_state=my_shipping['shipping_state']
        #    ship_address.shipping_zipcode=my_shipping['shipping_zipcode']
        #    ship_address.shipping_country=my_shipping['shipping_country']
        #    ship_address.save()

        amount = totals

        invoice_head = ['A', 'B', 'D', 'M', 'N', 'Q']
        invoice_tail = random.randint(3223, 99999)
        invoice_no = random.choice(invoice_head) + str(invoice_tail)
        invoice_date = datetime.now()

        # Create an Order
        if request.user.is_authenticated:
            # logged in
            user = request.user

            shipment = ShippingAddress.objects.filter(Q(shipping_id = shipping_id) & Q(user__id = user.id)).first()
            shipment.shipping_full_name = full_name
            shipment.shipping_address1 = shipping_address1
            shipment.shipping_address2 = shipping_address2
            shipment.shipping_city = city
            shipment.shipping_state = state
            shipment.shipping_zipcode = zip_code
            shipment.shipping_phone = phone
            shipment.shipping_email = email
            shipment.shipping_country  = country
            shipment.save()
            messages.success(request, "Your Shipment Address Info Has been Updatedd")

            # Create Order
            create_order = Orders.objects.create(user=user, name=full_name, email=email, phone=phone,address1=shipping_address1,
                                  address2=shipping_address2,amount=amount, city=city, state=state, zip_code=zip_code,
                                  invoice_no=invoice_no, invoice_date=invoice_date)
            create_order.save()

            update = OrderUpdate(order_id=create_order.order_id, update_desc="the order has been placed")
            update.save()
            thank = True
            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.product_id

                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.product_id:

                #     Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user,
                                                      quantity=value, price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]

            # Delete old cart from Profile of the User
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart=None)

            order_no = str(order_id)
            invoice_date=str(invoice_date.strftime("%d-%b-%Y %H:%M:%S"))


############################################# # Begin : PAYMENT INTEGRATION  ##########################
            #oid = str(order_id) + "ShopyCart"
            #MERCHANT_KEY = keys.MK
            #param_dict = {

            #    'MID': keys.MID,
            #    'ORDER_ID': oid,
            #    'TXN_AMOUNT': str(amount),
            #    'CUST_ID': email,
            #    'INDUSTRY_TYPE_ID': 'Retail',
            #    'WEBSITE': 'WEBSTAGING',
            #    'CHANNEL_ID': 'WEB',
            #    'CALLBACK_URL': 'http://127.0.0.1:8000/PayTm/handlerequest/',

            #}
            #param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            #return render(request, 'paytm.html', {'param_dict': param_dict})
############################################# # End  : PAYMENT INTEGRATION  ##########################

            html_content = get_template('orderemail.html').render(
                {'full_name': full_name, 'shipping_address': shipping_address, 'email': email,
                 'phone': phone, 'invoice_no': invoice_no, 'invoice_date':invoice_date,'order_no': order_no,
                 'cart_products': cart_products, 'quantities': quantities, 'totals': totals,
                 'prod_totals': prod_totals})

            send_mail_to_client(request,user=user, full_name=full_name, email=email, html_content=html_content)
            messages.success(request,
                             "Order Placed! Invoice sent to your registered mail id. Please take print of this page if mail not received by You.")

            return render(request, "orderemail.html",
                          {'full_name': full_name, 'shipping_address': shipping_address, 'email': email, 'phone': phone,
                           'invoice_no': invoice_no,'invoice_date':invoice_date,
                           'order_no': order_no, 'cart_products': cart_products, 'quantities': quantities,
                           'totals': totals, 'prod_totals': prod_totals})

        else:
            # not logged in
            # Create Order

            create_order = Orders.objects.create(user=None, name=full_name, email=email, phone=phone,
                                                 address1=shipping_address1,
                                                 address2=shipping_address2, amount=amount, city=city, state=state,
                                                 zip_code=zip_code,
                                                 invoice_no=invoice_no, invoice_date=invoice_date)
            create_order.save()

            update = OrderUpdate(order_id=create_order.order_id, update_desc="the order has been placed")
            update.save()
            thank = True

            # Add order items

            # Get the order ID
            order_id = create_order.pk

            # Get product Info
            for product in cart_products():
                # Get product ID
                product_id = product.product_id
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.product_id:

                # Create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value,
                                                      price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    print('Session Deelete..')
                    del request.session[key]
                    # Delete old cart from Profile of the User
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart=None)
            order_no=str(order_id)
            invoice_date = str(invoice_date.strftime("%d-%b-%Y %H:%M:%S"))

            html_content = get_template('orderemail.html').render(
                {'full_name': full_name, 'shipping_address': shipping_address, 'email': email,
                 'phone': phone, 'invoice_no':invoice_no, 'invoice_date':invoice_date, 'order_no':order_no,
                 'cart_products': cart_products, 'quantities': quantities, 'totals': totals,
                 'prod_totals': prod_totals})

            messages.success(request, "Order Placed! Invoice sent to your registered mail id. Please take print of this page if mail not received by You.")

            send_mail_to_client(request,user=None, full_name=full_name, email=email, html_content=html_content)

            return render(request, "orderemail.html",
                      {'full_name':full_name, 'shipping_address':shipping_address, 'email':email,'phone':phone, 'invoice_no':invoice_no, 'invoice_date':invoice_date,
                       'order_no':order_no,'cart_products':cart_products, 'quantities':quantities, 'totals':totals, 'prod_totals':prod_totals})

    else:
        messages.success(request, "Access Denied")
        return redirect('index')

@csrf_exempt
def handlerequest(request):
    MERCHANT_KEY = keys.MK
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a = response_dict['ORDERID']
            b = response_dict['TXNAMOUNT']
            rid = a.replace("ShopyCart", "")

            print(rid)
            filter2 = Orders.objects.filter(order_id=rid)
            print(filter2)
            print(a, b)
            for post1 in filter2:
                post1.oid = a
                post1.amountpaid = b
                post1.paymentstatus = "PAID"
                post1.save()
            print("run agede function")
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Orders.objects.filter(shipped=False)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Orders.objects.filter(order_id=num)
            # grab Date and time
            now = datetime.now()
            # update order
            order.update(shipped=True, date_shipped=now)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('index')

        return render(request, "not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Orders.objects.filter(shipped=True)
        if request.POST:
            num = request.POST['num']
            # grab the order
            order = Orders.objects.filter(order_id=num)
            # grab Date and time
            now = datetime.now()
            # update order
            order.update(shipped=False)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('index')


        return render(request, "shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')

def payment_orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Orders.objects.get(order_id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk).annotate(linetotal=F('quantity') * F('price'))

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == "true":
                # Get the order
                order = Orders.objects.filter(order_id=pk)
                # Update the status
                now = datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Get the order
                order = Orders.objects.filter(order_id=pk)
                # Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('index')

        return render(request, 'orders.html', {"order": order, "items": items})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')

