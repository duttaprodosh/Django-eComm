import time
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
import socket

def send_mail_to_client(request, user, full_name, email, html_content):
    socket.getaddrinfo('127.0.0.1', 8000)
    subject = 'Mail from Python djangoECommerce application.'

    from_email = settings.EMAIL_HOST_USER
    sender_email_id_password=settings.EMAIL_HOST_PASSWORD
    #recipient_list = ['duttaprodosh@gmail.com']
    recipient_list = list(email.split(" "))

    em = EmailMessage(subject=subject, body=html_content, from_email=from_email, to = recipient_list, cc=None, bcc=None, reply_to=None)
    em.content_subtype="html"
    try :
        em.send()
        messages.success(request, "Invoice Sent to Mail ID")
    except Exception as e:
        print("Exception Raised (Not able to send Html content in the email. :"+str(e))
        messages.success(request,"Mail Not Sent : Exception Raised - Not able to send Html content in the email. :"+str(e))
        em.content_subtype = "text"
        try :
            em.send()
            messages.success(request, "Invoice Sent to Mail ID")
        except Exception as e:
            print("Exception Raised (Not able to send Text email. :" + str(e))
            messages.success(request,"Mail Not Sent : Exception Raised - Not able to send Text email. :" + str(e))

