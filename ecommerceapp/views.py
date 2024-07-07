from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Contact, Product, Orders, OrderUpdate, OrderItem
from PayTm.models import ShippingAddress
from PayTm.forms  import ShippingForm
from django.contrib import messages
from .forms import SignUpForm, UserInfoForm, UpdateUserForm, ChangePasswordForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from math import ceil
from django.db.models import Q, F
from PayTm import Checksum, keys
MERCHANT_KEY= keys.MK
from django.views.decorators.csrf import  csrf_exempt
import json




# Create your views here.

def index(request):
    #products = Product.objects.all()
    #return render(request, "index_another.html", {'products':products})

    if request.method == "POST":
        searched = request.POST['searched']
        # Query The Products DB Model
        catprods = Product.objects.filter(Q(product_name__icontains=searched) | Q(desc__icontains=searched) | Q(category__in=searched)).values('category', 'product_id').order_by('category')
        # Test for null
        if not catprods:
            messages.success(request, "That Product Does Not Exist...Please try Again.")
            return render(request, "index.html", {})
    else:
        searched =""
        #category=request.GET["id"]
        #print(category)
        catprods = Product.objects.values('category', 'product_id').order_by('category')

    allProds=[]
    cats = {item['category'] for item in catprods}
    cats = sorted(cats)
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    return render(request, "index.html", {'allProds':allProds, 'search_value':searched})




def product(request,pk):
	product = Product.objects.get(product_id=pk)
	return render(request, 'product.html', {'product':product})

def contact(request):
    if request.method == "POST":
        try :
            con = request.POST
            name = request.POST.get('name')
            email = request.POST.get('email')
            desc =  request.POST.get('desc')
            phone = request.POST.get('phone')
            db_contact = Contact.objects.create(name=name, email=email, desc=desc, phone=phone)
            db_contact.save()
            messages.success(request, "New Contact has been Created.")
            return redirect('index')
        except Exception as e:
            print(e)
            messages.error(request, "Error : While creating New Contact."+str(e))
            return render(request, "contact.html")
    else:
        return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def orders(request, user_type):
        current_user = request.user.id

        if (user_type == 'user' or user_type == 'admin'):
            #shipment = ShippingAddress2.objects.get(user__id=current_user)
            orders = Orders.objects.filter(user__id=current_user).annotate(ship_date=F('date_shipped'),
                                                                          inv_date=F('invoice_date'), ord_amount=F('amount'))
            order_lines = OrderItem.objects.filter(user__id=current_user).annotate(linetotal=F('quantity') * F('price'))

            return render(request, "store_orders.html",
                          {'user_type': user_type, 'orders': orders, 'order_lines': order_lines})

        if (user_type == 'guest'):
            # shipment = ShippingAddress2.objects.get(user__id =None)
            orders = Orders.objects.filter(user__id=None).annotate(ship_date=F('date_shipped'),
                                                                  inv_date=F('invoice_date'), ord_amount=F('amount'))
            order_lines = OrderItem.objects.filter(user__id=None).annotate(linetotal=F('quantity') * F('price'))

            return render(request, "store_orders.html",
                          {'user_type': user_type, 'orders': orders, 'order_lines': order_lines})
        return redirect('index')

def update_user_info(request, update_token):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        usr_form = UpdateUserForm(request.POST or None, instance=current_user)
        profile = Profile.objects.get(user__id=request.user.id)
        if request.method == 'POST':
            ship_id = request.POST.get('shipping_id')
            shipment = ShippingAddress.objects.filter(shipping_id=ship_id).first()
        #shipment = ShippingAddress.objects.filter(user__id=request.user.id).all()
        form = UserInfoForm(request.POST or None, instance=profile)
        #shipping_form = ShippingForm(request.POST or None, instance=shipment)

############   Implementing the Ajax call from user_information.html
############   For method = 'POST' it will be Ajax Call and saving the changes in the database.
############   After saving updated User/Profile/Shipping Info it will not reload the page.
############   After successful/unsuccessfull form validatin and saving into dabase
############   It will retuen a JsonRespose with appropiate message to show in the HTM alert div.
        if (request.method=='POST'):
            if update_token=='user':
                if usr_form.is_valid():
                    usr_form.save()
                    messages.success(request, "Your User Info Has Been Updated!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your User Info Has Not Been Updated!!"+json.dumps(usr_form.errors.as_data()))
                    return JsonResponse({'success': False, 'errors': usr_form.errors})
            if update_token == 'profile':
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your Profile Info Has Been Updated!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your Profile Info Has Not Been Updated!!"+json.dumps(form.errors.as_data()))
                    return JsonResponse({'success': False, 'errors': form.errors})


            if update_token == 'ship_update':
                shipping_form = ShippingForm(request.POST, instance=shipment)
                if shipping_form.is_valid():
                   shipping_form.save()
                   messages.success(request, "Your Shipment Info Has Been updated!!")
                   return JsonResponse({'success': True})
                else:
                   messages.success(request, "Your Shipment Info Has Not Been updated!!"+json.dumps(shipping_form.errors.as_data()))
                   return JsonResponse({'success': False, 'errors': shipping_form.errors})

            if update_token == 'ship_delete':
                ship_count = ShippingAddress.objects.filter(user__id=current_user.id).count()
                if ship_count == None :
                    print('No Shipment')
                    return JsonResponse(
                        {'success': False, 'errors': 'Not a single Shipment Address Info Found!!'})
                if ship_count > 1 :
                    shipment.delete()
                    print('Shipment Deleted')
                    messages.success(request, "Your Shipment Info Has Been deleted!!")
                    return JsonResponse({'success': True})
                else :
                    messages.success(request, "Your Only One Shipment Address Info Cannot be deleted!! Atleast One Shipment Address Should Exists.")
                    print('Shipment Not Deleted')
                    return JsonResponse({'success': False, 'errors':'Your Only One Shipment Address Info Cannot be deleted!!'})

            if update_token == 'ship_create':
                shipping_form = ShippingForm(request.POST)
                if shipping_form.is_valid():
                   shipping_form.save()
                   ship_id = ShippingAddress.objects.filter(user__id=None).latest('shipping_id')
                   if ship_id is not None :
                       ship_id.user = current_user
                       ship_id.save()

                   messages.success(request, "Your New Shipment Info Has Been Created!!")
                   return JsonResponse({'success': True})
                else:
                   messages.success(request, "Your New Shipment Info Has Not Been Created!!"+json.dumps(shipping_form.errors.as_data()))
                   return JsonResponse({'success': False, 'errors': shipping_form.errors})

            shipment = ShippingAddress.objects.filter(user__id=request.user.id).order_by('shipping_id').all()
            paginator = Paginator(shipment, 1)  # Show 1 Shipping Address per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, "user_information.html",
                          {'profile': profile, 'shipment_rec': shipment, 'page_obj': page_obj})
            #if form.is_valid()  or shipping_form.is_valid():
            #    # Save original form
            #    form.save()
                # Save shipping form
            #    shipping_form.save()
            #current_user = User.objects.get(id=request.user.id)
            #profile = Profile.objects.get(user__id=request.user.id)
            #shipment = ShippingAddress2.objects.get(user__id=request.user.id)

            #return render(request, "user_information.html", {'user':current_user, 'profile':profile, 'shipment':shipment})
        else :
            shipment = ShippingAddress.objects.filter(user__id=request.user.id).order_by('shipping_id').all()
            paginator = Paginator(shipment, 1)  # Show 1 Shipping Address per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, "user_information.html", {'profile': profile, 'shipment_rec': shipment, 'page_obj': page_obj})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('index')

def invoice(request, full_name, shipping_address, email, phone, invoice_no, invoice_date, order_no, totals):
    current_user = request.user.id

    quantities = {}
    prod_totals = {}
    order_lines = OrderItem.objects.filter(order__order_id=order_no).annotate(linetotal=F('quantity') * F('price'))
    product_ids = []
    for lines in order_lines:
        product_ids.append(lines.product.pk)

    products = Product.objects.filter(product_id__in=product_ids)
    for line in order_lines:
        quantities[str(line.product.product_id)]=line.quantity
        prod_totals[str(line.product.product_id)]=line.linetotal
    html_content = get_template('orderemail.html').render(
                {'full_name': full_name, 'shipping_address': shipping_address, 'email': email, 'phone': phone,
                'invoice_no': invoice_no, 'invoice_date': invoice_date,
                'order_no': order_no, 'cart_products': products, 'quantities': quantities, 'totals': totals,
                'prod_totals': prod_totals})
    #send_mail_to_client(request,None, full_name, email, phone, shipping_address, totals, html_content)
    return render(request, "orderemail.html",
                  {'full_name': full_name, 'shipping_address': shipping_address, 'email': email, 'phone': phone,
                   'invoice_no': invoice_no, 'invoice_date': invoice_date,
                   'order_no': order_no, 'cart_products': products, 'quantities':quantities, 'totals': totals, 'prod_totals': prod_totals  })



def profile1(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)
    rid = ""
    for i in items:
        print(i.oid)
        # print(i.order_id)
        myid = i.oid
        rid = myid.replace("ShopyCart", "")
        print(rid)
    status = OrderUpdate.objects.filter(order_id=int(rid))
    for j in status:
        print(j.update_desc)

    context = {"items": items, "status": status}
    # print(currentuser)
    return render(request, "profile.html", context)