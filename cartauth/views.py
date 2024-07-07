from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from .utils import send_mail_to_client
from random import randint
from django.db.models import Q
import json
from ecommerceapp.models import Profile
from cart.cart import Cart

# Create your views here.
def user_profile(request):
    username = request.user
    if request.method == 'GET':
        user = User.objects.filter(username=username).first()
        return render(request,'authentication/user_profile.html', {'user':user})
    else :
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user = User.objects.filter(username=username).first()
        user.first_name = first_name
        user.last_name  = last_name
        user.email      = email

        user.save()
        messages.success(request, "User Profile Successfully Updated.")
        return redirect('index')

import uuid
def forget_password(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email    = request.POST.get('email')
            print('User Name : '+username+'  Email :'+email)
            if  (username != None) and (email != None):
                user = User.objects.filter(Q(username=username ) & Q(email=email)).first()

            if  (username != None) and (email == None):
                print('User2 : Param - '+username+' email - '+email)
                user = User.objects.filter(username=username).first()

            if  (email != None) and (username == None):
                user = User.objects.filter(email=email).first()

            if user == None:
                print('None User : Param - '+username+'  Email : '+email)
                user = User.objects.filter(username=username).first()
                if user == None :
                    user = User.objects.filter(email=email).first()
                    if user == None :
                        messages.success(request, "User Not Found !!")
                        return redirect('forget_password')

            if user != None:
               full_name = user.first_name
               token = str(uuid.uuid4())
               otp = str(randint(1000, 9999))
               request.session['otp'] = otp
               request.session['token'] = token
               subject = "Your Forget Password Link."
               reset_link = 'http://127.0.0.1:8000/update_password/'
               reset_email_link = 'http://127.0.0.1:8000/cartauth/update_password_emaillink/'+str(user.id)+'/'+token+'/'
               html_content = get_template('authentication/forgetPass.html').render(
                        {'user': user.username, 'full_name': full_name, 'email': user.email, 'link': reset_email_link,
                         'user_id': str(user.id), 'token': token, 'otp':otp})

               send_mail_to_client(request,user=None,full_name=full_name, email=user.email, html_content=html_content)
               messages.success(request, "Your Password Reset Link sent to Your Email Id. Please click on Reset Link in the Email as forwared")
               return redirect('index')
        else :
            print('Get : Rendering first time forget_password.html')
            return render(request, "authentication/forget_password.html")
            #return render(request, "forget_password.html", {'user':user,'full_name': full_name, 'email': user.email, 'link':reset_link, 'user_id':str(user.id), 'token':token})
            #return True

    except Exception as e:
        print(e)
        messages.error(request, " Oops ! Error : "+str(e))
        return redirect("index")

def update_password_emaillink(request,userid,token):
    if request.method == 'GET':
        print('userid in update_password_emaillink : '+userid+' token : '+token)
        return render(request, 'authentication/otp_input.html', {'userid':str(userid), 'token': token } )
    else :

        try :

            current_user = User.objects.get(pk=userid)
            db_token = request.session.get('token')
            db_otp   = request.session.get('otp')
            otp      = request.POST.get('otp')

            if db_token == token and db_otp == otp :
                    form = ChangePasswordForm(current_user)
                    return render(request, "authentication/update_password.html", {'form': form, 'token': token, 'userid': userid, 'user':current_user})
            else:
                    messages.success(request,'OTP Mismatch : Incorrect OTP has been inputted. Please Try Again.')
                    return render(request, 'authentication/otp_input.html', {'userid':str(userid), 'token': token } )
        except Exception as e:
            print(e)
            messages.error(request,e)
            return redirect('index')

def update_password(request):

###################    Reset of Password without Logged in User
###################    By Username, User are requested to click
###################    on the Reset Password Link forwarded to his/her's Email Id
    try :
        if request.method == 'POST' and not(request.user.is_authenticated):
            token = request.POST.get('token')
            user_id = request.POST.get('user_id')

            if user_id != None :
                print('Profile User Id : '+str(user_id))
                db_token = request.session.get('token')
                user_id_reset = user_id


            if user_id_reset != None or token == db_token:
                current_user = User.objects.get(pk=user_id_reset)
                form = ChangePasswordForm(current_user, request.POST)

                if form.is_valid():
                    form.save()
                    current_user.password = request.POST.get('new_password1')
                    #current_user.save()
                    messages.success(request, "Your Password Has Been Updated...Please Log-In with Your New Password. ")
                    user = authenticate(request, username=current_user.username, password=current_user.password)
                    if user is None :
                        print('Authentication Failure...')
                    if user is not None:
                        auth_login(request, user)
                    return redirect('index')
                else:
                    for error in list(form.errors.values()):
                        messages.error(request, error)
                    return render(request, "authentication/update_password.html", {'form': form, 'userid':user_id_reset, 'token':token})
                return render(request, "authentication/update_password.html", {'form': form,'userid':user_id_reset, 'token':token})
    except Exception as e:
        print(e)
        print('User Id (exceptiom) :'+str(user_id_reset)+' token :'+token)
        messages.error(request, e)
        return render(request, "authentication/update_password.html", {'userid':user_id_reset, 'token':token})
################ End of Password Reset without User Login  ########################

##########  Password Reset Once user has been authenticated by his Login credential ##########
    if (request.user.is_authenticated):
        current_user = request.user
        # Did they fill out the form
        if request.method  == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                auth_login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "authentication/update_password.html", {'form':form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('index')



def login(request):
    if request.method == "POST":
        username   = request.POST.get('username')
        password  = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form1 = auth_login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)

            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop thru the cart and add the items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request, ("You are successfully Logged in as User name :"+username))
            return redirect('index')
        else:
            messages.info(request, f'User Account does not exist. Please use Your Correct User Name and Password to Log In.')
    return render(request, "authentication/login.html")


def signup(request):

    if request.method == "POST":

        #    first_name = request.POST.get('first_name')
        #    last_name = request.POST.get('last_name')
        #    username   = request.POST.get('username')
        #    password1  = request.POST.get('password1')
        #    password2  = request.POST.get('password2')
        #    email = request.POST.get('email')
        #    form = SignUpForm(username=username, first_name=first_name, last_name=last_name, email=email, password1=password1, password2=password2)
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(request,username=username, password=password)
            if user is not None:
                form1 = auth_login(request, user)
                messages.success(request, ("Username Created - You are successfully Logged in..."))
                if request.user.is_authenticated :
                    return redirect('update_user_info', update_token=' ')
                else :
                    return redirect('index')
            else :
                messages.info(request, f'User Account does not exists. plz Sign Up')
        else:
            messages.success(request, "Signup Error !!"+str(form.errors.as_data()))
            return render(request, "authentication/signup.html")
    else:
        form = SignUpForm()
    return render(request, "authentication/signup.html", {"form": form})



def logout(request):
    if request.user.is_authenticated :
        username = request.user.username
        auth_logout(request)
        messages.success(request, ("Thanks for Your Shopping !! You Have been Logged Out as User Name :" + username))
    return redirect('index')
