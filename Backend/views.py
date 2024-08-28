import os

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from Webapp.models import Mechanics,logintable,ServiceCenter,feedback,Order,Cart
from django.contrib import messages
import datetime
from Backend.models import Category,Products
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
def admin_login(request):
    return render(request,"admin_login.html",)

def loginpage(request):
    if request.method=="POST":
        un=request.POST.get("username")
        pw=request.POST.get("password")
        if User.objects.filter(username__contains=un).exists():
            a=authenticate(username=un,password=pw)
            if a is not None:
                login(request,a)
                request.session['username']=un
                request.session['password']=pw
                messages.success(request,"Welcome....")
                return redirect(admin_index)
            else:
                messages.warning(request,"Invalid username and password")
                return redirect(admin_login)
        else:
            messages.warning(request, "username not found")
            return redirect(admin_login)

def adminlogout(request):
        del request.session['username']
        del request.session['password']
        messages.success(request, "Logout success")
        return redirect(admin_login)

def forgot_pwd(request):
    return redirect()

@login_required
def admin_index(req):
    dat=datetime.datetime.now()
    accepted_count = Mechanics.objects.filter(Type='accepted').count()
    rejected_count = Mechanics.objects.filter(Type='rejected').count()
    pending_count = Mechanics.objects.filter(Type='pending').count()
    # Dummy data (replace with your actual data retrieval)
    categories = ['accepted', 'rejected', 'pending']
    counts = [accepted_count, rejected_count, pending_count]  # Replace with your actual counts
    plt.figure(figsize=(8, 6))
    plt.bar(categories, counts, color=['green', 'red', 'orange'])
    plt.xlabel('Request Status')
    plt.ylabel('Count')
    plt.title('Request Status Counts')

    # Plotting
    media_directory = os.path.join(os.getcwd(), 'media')
    if not os.path.exists(media_directory):
        os.makedirs(media_directory)

    # Save the plot as PNG image in the media folder
    img_path = os.path.join(media_directory, 'request_status_counts.png')
    plt.savefig(img_path)

    # Pass the image path to the template
    context = {
        "dat": dat,
        'img_path': '/media/request_status_counts.png'  # Note: Ensure correct URL based on your project setup
    }

    return render(req,"index.html",context)

def view_mechanic(req):
    data=Mechanics.objects.all()
    d="Mechanics"
    d1="Rejected"
    d2="pending"
    return render(req,"view_Mechanic.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def approve_mech(request,mid):
    Mech = get_object_or_404(Mechanics, Mechid=mid)

    # Update the mechanic's type
    Mech.Type = "Mechanics"
    Mech.save()

    # Check if the update was successful
    if Mech.Type == 'Mechanics':
        subject = 'Request Confirmation'
        html_message = render_to_string('request_confirm.html', {'user': Mech})
        plain_message = strip_tags(html_message)
        from_email = 'getmehelp73@gmail.com'
        to_email = Mech.Email

        try:
            # Send the email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        except Exception as e:
            # Handle any errors that occur during email sending
            print(f"Error sending email: {e}")
            # Optionally, log the error or notify the user

    return redirect(view_mechanic)
def reject_mech(request,mid):
    Mech = get_object_or_404(Mechanics, Mechid=mid)

    # Update the mechanic's type
    Mech.Type = "Rejected"
    Mech.save()

    # Check if the update was successful
    if Mech.Type == 'Rejected':
        subject = 'Request Confirmation'
        html_message = render_to_string('request_reject.html', {'user': Mech})
        plain_message = strip_tags(html_message)
        from_email = 'getmehelp73@gmail.com'
        to_email = Mech.Email

        try:
            # Send the email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        except Exception as e:
            # Handle any errors that occur during email sending
            print(f"Error sending email: {e}")
    return redirect(view_mechanic)

def view_approved_mech(req,type):
    data=Mechanics.objects.filter(Type=type)
    d = "Mechanics"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"approved_mech.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_rejected_mech(req,type):
    data=Mechanics.objects.filter(Type=type)
    d = "Mechanics"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"rejected_mech.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_pending_mech(req,type):
    data=Mechanics.objects.filter(Type=type)
    d = "Mechanics"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"pending_mech.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_servicecentre(req):
    data=ServiceCenter.objects.all()
    d="service"
    d1="Rejected"
    d2="pending"
    return render(req,"view_servicecenter.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def approve_servicecentre(request,sid):
    ServiceCenter.objects.filter(id=sid).update(Type="service")
    Service = get_object_or_404(ServiceCenter, id=sid)

    # Update the mechanic's type
    Service.Type = "service"
    Service.save()

    # Check if the update was successful
    if Service.Type == 'service':
        subject = 'Request Confirmation'
        html_message = render_to_string('service_accept.html', {'user': Service})
        plain_message = strip_tags(html_message)
        from_email = 'getmehelp73@gmail.com'
        to_email = Service.Email

        try:
            # Send the email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        except Exception as e:
            # Handle any errors that occur during email sending
            print(f"Error sending email: {e}")
    return redirect(view_servicecentre)
def reject_servicecentre(request,sid):
    ServiceCenter.objects.filter(id=sid).update(Type="service")
    Service = get_object_or_404(ServiceCenter, id=sid)

    # Update the mechanic's type
    Service.Type = "Rejected"
    Service.save()

    # Check if the update was successful
    if Service.Type == 'Rejected':
        subject = 'Request Confirmation'
        html_message = render_to_string('service_reject.html', {'user': Service})
        plain_message = strip_tags(html_message)
        from_email = 'getmehelp73@gmail.com'
        to_email = Service.Email

        try:
            # Send the email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        except Exception as e:
            # Handle any errors that occur during email sending
            print(f"Error sending email: {e}")
    return redirect(view_servicecentre)

def view_approved_servicecentre(req,type):
    data=ServiceCenter.objects.filter(Type=type)
    d = "service"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"approved_center.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_rejected_servicecentre(req,type):
    data=ServiceCenter.objects.filter(Type=type)
    print(data)
    d = "service"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"rejected_center.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_pending_servicecentre(req,type):
    data=ServiceCenter.objects.filter(Type=type)
    print(data)
    d = "service"
    d1 = "Rejected"
    d2 = "pending"
    return render(req,"pending_center.html",{"data":data,"d":d,"d1":d1,"d2":d2})

def view_feedback(request):
    data=feedback.objects.all()
    return render(request,"view_feedback.html",{"data":data})

def add_category(request):
    return render(request,"add_category.html")

def save_category(request):
    if request.method=="POST":
        name=request.POST.get("name")
        pic=request.FILES['picture']
        descr=request.POST.get("description")
        Category(Categoryname=name,Image=pic,Description=descr).save()
        return redirect(add_category)
def view_category(request):
    data=Category.objects.all()
    return render(request,"view_category.html",{"data":data})

def edit_cat(request,cid):
    data=Category.objects.get(id=cid)
    return render(request,"edit_category.html",{"data":data})

def update_category(request,cid):
    if request.method=="POST":
        name=request.POST.get("name")
        descr=request.POST.get("description")
        try:
            pic = request.FILES['picture']
            fs=FileSystemStorage()
            pic=fs.save(pic.name,pic)
        except MultiValueDictKeyError:
            pic=Category.objects.get(id=cid).Image
        Category.objects.filter(id=cid).update(Categoryname=name,Image=pic,Description=descr)
        return redirect(view_category)
def delete_cat(request,cid):
    Category.objects.filter(id=cid).delete()
    return redirect(view_category)
def add_product(request):
    data=Category.objects.all()
    return render(request,"add_products.html",{'data':data})
def save_product(request):
    if request.method=="POST":
        pname=request.POST.get("pname")
        category=request.POST.get("category")
        price=request.POST.get("price")
        pic = request.FILES['picture']
        des=request.POST.get("description")
        Products(Productname=pname,Category=category,Price=price,Image=pic,Description=des).save()
        return redirect(add_product)

def view_product(request):
    data=Products.objects.all()
    return render(request,"view_products.html",{'data':data})

def edit_product(request,pid):
    data=Products.objects.get(id=pid)
    cat=Category.objects.all()
    return render(request,"editproduct.html",{"data":data,"cat":cat})

def update_product(request,pid):
    if request.method=="POST":
        pname=request.POST.get("pname")
        category=request.POST.get("category")
        price=request.POST.get("price")
        des=request.POST.get("description")
        try:
            pic = request.FILES['picture']
            fs=FileSystemStorage()
            pic=fs.save(pic.name,pic)
        except MultiValueDictKeyError:
            pic=Products.objects.get(id=pid).Image
        Products.objects.filter(id=pid).update(Productname=pname,Category=category,Price=price,Image=pic,Description=des)
        return redirect(view_product)

def delete_product(request,pid):
    Products.objects.filter(id=pid).delete()
    return redirect(view_product)

# def request_status_counts(request):
#     # Count requests for each status
#     accepted_count = Mechanics.objects.filter(status='accepted').count()
#     rejected_count = Mechanics.objects.filter(status='rejected').count()
#     pending_count = Mechanics.objects.filter(status='pending').count()
#
#     context = {
#         'accepted_count': accepted_count,
#         'rejected_count': rejected_count,
#         'pending_count': pending_count,
#     }
#
#     return render(request, 'request_status_counts.html', context)

import matplotlib.pyplot as plt
import numpy as np

def mechanics_stats(request):
    accepted_count = Mechanics.objects.filter(status='accepted').count()
    rejected_count = Mechanics.objects.filter(status='rejected').count()
    pending_count = Mechanics.objects.filter(status='pending').count()
    # Dummy data (replace with your actual data retrieval)
    categories = ['accepted', 'rejected', 'pending']
    counts = [accepted_count, rejected_count, pending_count]  # Replace with your actual counts

    # Plotting
    plt.bar(categories, counts)
    plt.xlabel('Request Type')
    plt.ylabel('Number of Requests')
    plt.title('Mechanics Requests Overview')
    plt.grid(True)

    # Save the plot as PNG image in a temporary location (optional)
    plt.savefig('media/mechanics_requests.png')

    # Pass the image path to the template
    img_path = 'media/mechanics_requests.png'

    return render(request, 'mechanics_stats.html', {'img_path': img_path})
def request_status_counts(request):
    accepted_count = Mechanics.objects.filter(status='accepted').count()
    rejected_count = Mechanics.objects.filter(status='rejected').count()
    pending_count = Mechanics.objects.filter(status='pending').count()
    # Dummy data (replace with your actual data retrieval)
    categories = ['accepted', 'rejected', 'pending']
    counts = [accepted_count, rejected_count, pending_count]  # Replace with your actual counts

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.bar(categories, counts, color=['green', 'red', 'orange'])
    plt.xlabel('Request Status')
    plt.ylabel('Count')
    plt.title('Request Status Counts')

    # Save the plot as PNG image (optional)
    plt.savefig('media/request_status_counts.png')

    # Pass the image path to the template
    img_path = 'media/request_status_counts.png'

    return render(request, 'index.html', {'img_path': img_path})
def order_status_view(request):
    orders = Order.objects.all()  # Fetch all orders
    order_data = []

    for order in orders:
        cart_items = Cart.objects.filter(username=order.uname)
        order_data.append({
            'order': order,
            'cart_items': cart_items
        })

    return render(request, 'order_status.html', {'order_data': order_data})

@csrf_exempt
def update_order_status_ajax(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        try:
            order = Order.objects.get(id=order_id)
            if status in dict(Order.STATUS_CHOICES).keys():
                order.status = status
                order.save()
                if status == 'Confirmed' or 'Shipped' or 'Cancelled' or 'Delivered':  # Replace 'confirmed' with your actual status
                    subject = 'Order Confirmation'
                    html_message = render_to_string('order_confirmation.html',
                                                    {'order': order, 'user': order.user})
                    plain_message = strip_tags(html_message)
                    from_email = 'getmehelp73@gmail.com'
                    to_email = order.Email

                    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

                return JsonResponse({'message': 'Order status updated successfully.'})
            else:
                return JsonResponse({'error': 'Invalid status value.'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)