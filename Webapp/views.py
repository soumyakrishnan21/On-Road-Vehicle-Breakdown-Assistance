import math

import app
import pytz
import razorpay
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from geopy import Nominatim
from Backend.models import Products
from django.contrib.auth.decorators import login_required
import urllib.parse
from django.shortcuts import render, get_object_or_404

from Webapp.models import Mechanics, logintable, ServiceCenter, feedback, userdatas, Service, Cart, Order, UserRequests, \
    Mechpayment, PINLocation, Booking, servicefeedback, FAQ

from Backend.models import chatmessage, Category
from django.http import JsonResponse, HttpResponse

import folium
import geocoder
import time
import requests

from django.contrib.auth import views as auth_views

from .utils import generate_token  # Import the utility function
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class CustomLoginView(auth_views.LoginView):
    template_name = 'mechanic/signin.html'


def get_current_gps_coordinates():
    g = geocoder.ip('me')  # this function is used to find the current information using our IP Add
    if g.latlng is not None:  # g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None


from django import forms
from .tasks import get_bot_response


class ChatForm(forms.Form):
    user_question = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}), label='Ask me anything:')


def indexpage(request):
    response = None
    form = ChatForm()
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_question = form.cleaned_data['user_question']
            # Call the Celery task
            result = get_bot_response.delay(user_question)
            bot_response = result.get()  # Wait for the result

            response = {
                'user_question': user_question,
                'bot_response': bot_response,
            }

    # return render(request, 'home.html', {'form': form, 'response': response})

    data = feedback.objects.all()
    print(data)
    # data=Mechanics.objects.all()
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
    geolocator = Nominatim(user_agent="location_app")
    location = geolocator.reverse((latitude, longitude), language='en')
    print(location)
    Mechanics = "Mechanics"
    service = "service"

    # user="user"
    userid = request.session.get("Userid")
    # Type=request.session("Type")
    # print(Type)
    # user_type = Mechanics.objects.filter(Type=Mechanics)  # Assuming you have a user_type field in your user model
    # user_type = request.session.get('Type')
    return render(request, "indexuser.html",
                  {'location': location, 'lat': latitude, 'long': longitude, 'data': data, 'form': form,
                   'response': response, "userid": userid})


def aboutus(request):
    data = feedback.objects.all()
    return render(request, "about_us.html", {"data": data})


def faq_view(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq.html', {'faqs': faqs})


def service_page(request):
    return render(request, "services.html")


def view_feedback_user(request):
    data = feedback.objects.all()
    return render(request, "about_us.html", {"data": data})


def term_condition(request):
    data = feedback.objects.all()
    return render(request, "terms_coditions.html", {"data": data})


def mapview(request):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
        mechanic_latitude, mechanic_longitude = None, None

    # Reverse geocoding to get location details
    location = None
    if mechanic_latitude is not None and mechanic_longitude is not None:
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
        print(location)

    # Retrieve mechanic's requests
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Pending').order_by('-timestamp')

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        if latitude is None or longitude is None:
            continue
        print(latitude, longitude)
        timestamp_str = format(timestamp, 'Y-m-d H:i:s')

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            # 'latitude': latitude,
            # 'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp_str,
            'payment_status': payment_status,
            'mechanic_latitude': mechanic_latitude,
            'mechanic_longitude': mechanic_longitude,
            'user_latitude': latitude,
            'user_longitude': longitude
        })

        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

            # Add markers for user and mechanic locations
        folium.Marker(
            [latitude, longitude],
            tooltip=f'User: {username}, Status: {status}',
            icon=folium.Icon(color='blue', icon='user', prefix='fa')
        ).add_to(user_map)

        if mechanic_latitude and mechanic_longitude:
            folium.Marker(
                [mechanic_latitude, mechanic_longitude],
                tooltip='Mechanic Location',
                icon=folium.Icon(color='red', icon='wrench', prefix='fa')
            ).add_to(user_map)

            # Add routing between mechanic's location and user's location
            folium.PolyLine(
                locations=[(mechanic_latitude, mechanic_longitude), (latitude, longitude)],
                color='blue',
                weight=2.5,
                opacity=1
            ).add_to(user_map)
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': json.dumps(data),

    }
    return render(request, "mechanic/map.html", context)


# .................Mechanic.....................
def mech_index(request):
    data = feedback.objects.all()
    print(data)
    return render(request, "mech_index.html", {"data": data})


def mech(req):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
    geolocator = Nominatim(user_agent="location_app")
    location = geolocator.reverse((latitude, longitude), language='en')
    print(location)
    return render(req, "Mechanic/Mechanic_register.html", {'lat': latitude, 'long': longitude})


def view_request_from_user(request):
    status = "Accepted"
    status1 = "Rejected"
    status2 = "Pending"

    # Get mechanic's current GPS coordinates
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
        mechanic_latitude, mechanic_longitude = None, None

    # Reverse geocoding to get location details
    location = None
    if mechanic_latitude is not None and mechanic_longitude is not None:
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
        print(location)

    # Retrieve mechanic's requests
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Pending').order_by('-timestamp')

    data = []
    user_map = None
    # user_ids = set()  # To ensure unique user IDs
    user_idd = request.user.id
    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        description = req.description
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        if latitude is None or longitude is None:
            continue

            # Collect unique user IDs
        # user_ids.add(user_id)
        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status,
            'mechanic_latitude': mechanic_latitude,
            'mechanic_longitude': mechanic_longitude,
            'user_latitude': latitude,
            'user_longitude': longitude,
            'description': description,
        })

        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

            # Add markers for user and mechanic locations
        folium.Marker(
            [latitude, longitude],
            tooltip=f'User: {username}, Status: {status}',
            icon=folium.Icon(color='blue', icon='user', prefix='fa')
        ).add_to(user_map)

        if mechanic_latitude and mechanic_longitude:
            folium.Marker(
                [mechanic_latitude, mechanic_longitude],
                tooltip='Mechanic Location',
                icon=folium.Icon(color='red', icon='wrench', prefix='fa')
            ).add_to(user_map)

            # Add routing between mechanic's location and user's location
            folium.PolyLine(
                locations=[(mechanic_latitude, mechanic_longitude), (latitude, longitude)],
                color='blue',
                weight=2.5,
                opacity=1
            ).add_to(user_map)
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': data,
        'status': status,
        "status1": status1,
        "status2": status2,
        'user_id': user_idd,
        'mid': mid
    }

    return render(request, "Mechanic/view_request.html", context)


def view_request_details(request, rid):
    request_details = get_object_or_404(UserRequests, id=rid)
    mech_payment = Mechpayment.objects.filter(Reqid=rid).first()
    context = {
        'request_details': request_details,
        'mech_payment': mech_payment,
    }

    return render(request, 'Mechanic/detailed_request.html', context)


def accept_request_from_user(request, rid, uid):
    UserRequests.objects.filter(id=rid).update(status="Accepted")
    mid = request.session.get('Mechid')
    print(mid)
    Mechpayment(Userid=uid, Reqid=rid, Mechid=mid, status='Pending').save()
    # mechanic_id = request.user.id

    # Fetch the request and user data
    # request_obj = get_object_or_404(UserRequests, id=rid)
    # user_data = get_object_or_404(userdatas, Userid=request_obj.Userid)

    request_obj = get_object_or_404(UserRequests, id=rid)
    user_data = get_object_or_404(userdatas, Userid=uid)
    UserRequests.objects.filter(id=rid).update(status="Accepted")
    mid = request.session.get('Mechid')
    print(mid)
    Mechpayment(Userid=uid, Reqid=rid, Mechid=mid, status='Pending').save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_data.Userid}",
        {
            'type': 'notify_user',
            'message': f"Your request has been accepted by the mechanic.",
        }
    )

    messages.success(request, "Request accepted successfully.")
    return redirect(view_request_from_user)


def accept_to_workdone(request, rid):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # instance = get_object_or_404(Mechpayment, pk=rid)
        # instance.amount = amount
        # instance.save()
        Mechpayment.objects.filter(Reqid=rid).update(Amount=amount)
        UserRequests.objects.filter(id=rid).update(status="Accepted")
        mid = request.session.get('Mechid')
        print(mid)
        UserRequests.objects.filter(id=rid).update(status='Work done')
        return JsonResponse({'success': True})

    # return redirect(view_request_from_user)
    return JsonResponse({'success': False})


def update_amount(request, rid):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        instance = get_object_or_404(Mechpayment, pk=rid)
        instance.amount = amount
        instance.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def view_workdone_request(request):
    status = "Accepted"
    status1 = "Rejected"
    status2 = "Pending"

    # Get mechanic's current GPS coordinates
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
        mechanic_latitude, mechanic_longitude = None, None

    # Reverse geocoding to get location details
    location = None
    if mechanic_latitude is not None and mechanic_longitude is not None:
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
        print(location)

    # Retrieve mechanic's requests
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Work done')

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        if latitude is None or longitude is None:
            continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status
        })

        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

        # Add markers for user and mechanic locations
        folium.Marker([latitude, longitude], tooltip=f'User: {username}, Status: {status}').add_to(user_map)
        folium.Marker([mechanic_latitude, mechanic_longitude], tooltip='Mechanic Location').add_to(user_map)

        # Add routing between mechanic's location and user's location
        if latitude is not None and longitude is not None:
            folium.PolyLine(locations=[(mechanic_latitude, mechanic_longitude), (latitude, longitude)],
                            color='blue', weight=2.5, opacity=1).add_to(user_map)

    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': data,
        'status': status,
        "status1": status1,
        "status2": status2
    }

    return render(request, "Mechanic/workdone.html", context)


def view_single_request(request, uid):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")

    geolocator = Nominatim(user_agent="location_app")
    location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
    print(location)
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Pending')
    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        data.append(
            {
                'userid': user_id,
                'reqid': reqid,
                'username': username,
                'latitude': latitude,
                'longitude': longitude,
                'Mobile': Mobile,
                'status': status,
                'timestamp': timestamp
            }
        )
        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

            # Add markers for user and mechanic locations
        folium.Marker([latitude, longitude], tooltip=f'User: {username}, Status: {status}').add_to(user_map)
        folium.Marker([mechanic_latitude, mechanic_longitude], tooltip='Mechanic Location').add_to(user_map)

        # Add routing between mechanic's location and user's location
    if len(data) > 0:
        first_request = data[0]
        user_location = [first_request['latitude'], first_request['longitude']]
        folium.PolyLine(locations=[(mechanic_latitude, mechanic_longitude), user_location],
                        color='blue', weight=2.5, opacity=1).add_to(user_map)

        # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': data,
    }

    return render()


def reject_request_from_user(request, rid, uid):
    UserRequests.objects.filter(id=rid).update(status="Rejected")
    user_id = uid
    user_request = {
        'message': 'Your request has been rejected.'
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_notification',
            'message': json.dumps(user_request)
        }
    )
    messages.error(request, "Request rejected successfully.")
    return redirect(view_request_from_user)


def accepted_requests(request):
    statuss = "Accepted"
    status1 = "Rejected"
    status2 = "Pending"

    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")

    if mechanic_latitude is not None and mechanic_longitude is not None:
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
        print(location)

    # Retrieve mechanic's requests
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Accepted')

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        if latitude is None or longitude is None:
            continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status,
            'statuss': statuss,
            'mid': mid

        })

        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

        # Add markers for user and mechanic locations
        folium.Marker([latitude, longitude], tooltip=f'User: {username}, Status: {status}').add_to(user_map)
        folium.Marker([mechanic_latitude, mechanic_longitude], tooltip='Mechanic Location').add_to(user_map)

        # Add routing between mechanic's location and user's location
        if latitude is not None and longitude is not None:
            folium.PolyLine(locations=[(mechanic_latitude, mechanic_longitude), (latitude, longitude)],
                            color='blue', weight=2.5, opacity=1).add_to(user_map)

    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': data,
        'mid': mid

    }
    print(context)
    return render(request, "Mechanic/Accepted_requests.html", context)


def rejected_requests(request):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        mechanic_latitude, mechanic_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {mechanic_latitude}")
        print(f"Longitude: {mechanic_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")

    geolocator = Nominatim(user_agent="location_app")
    location = geolocator.reverse((mechanic_latitude, mechanic_longitude), language='en')
    print(location)
    mid = request.session.get('Mechid')
    print(mid)
    mechanic_requests = UserRequests.objects.filter(Mechid=mid, status='Rejected')
    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Userid
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        location = user_data.Location
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        data.append(
            {
                'userid': user_id,
                'reqid': reqid,
                'username': username,
                'latitude': latitude,
                'longitude': longitude,
                'Mobile': Mobile,
                'status': status,
                'timestamp': timestamp
            }
        )
        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

            # Add markers for user and mechanic locations
        folium.Marker([latitude, longitude], tooltip=f'User: {username}, Status: {status}').add_to(user_map)
        folium.Marker([mechanic_latitude, mechanic_longitude], tooltip='Mechanic Location').add_to(user_map)

        # Add routing between mechanic's location and user's location
    if len(data) > 0:
        first_request = data[0]
        user_location = [first_request['latitude'], first_request['longitude']]
        folium.PolyLine(locations=[(mechanic_latitude, mechanic_longitude), user_location],
                        color='blue', weight=2.5, opacity=1).add_to(user_map)

        # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': data,
    }
    print(context)
    return render(request, "Mechanic/Rejected_requests.html", context)


def get_location_by_address(address):
    """This function returns a location as raw from an address
    will repeat until success"""
    time.sleep(1)
    try:
        return app.geocode(address).raw
    except:
        return get_location_by_address(address)


def get_coordinates_from_address(address):
    geolocator = Nominatim(user_agent="location_app")
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None, None


def mech_reg(request):
    if request.method == "POST":
        name = request.POST.get("name")
        age = request.POST.get("age")
        address = request.POST.get("address")
        mob = request.POST.get("mobile")
        veh = request.POST.get("type")
        pl = request.POST.get("place")
        lat = request.POST.get("lat")
        long = request.POST.get("long")
        pic = request.FILES['pic']
        uname = request.POST.get("uname")
        email = request.POST.get("email")
        pw = request.POST.get("password")

        if Mechanics.objects.filter(Username=uname).exists():
            messages.warning(request, "Username already exists.")
            return redirect('mechlogin')  # Adjust the URL name to match your configuration

            # Fetch coordinates from address
        latitude, longitude = get_coordinates_from_address(address)
        # if latitude is None or longitude is None:
        #     messages.error(request, "Location not found.")
        #     return redirect('mechlogin')  # Adjust the URL name to match your configuration

        # Reverse geocode to get location details
        # geolocator = Nominatim(user_agent="location_app")
        # location = geolocator.reverse((latitude, longitude), language='en')
        # if location:
        #     print(f"Location found: {location.address}")
        # else:
        #     messages.error(request, "Location could not be reverse geocoded.")
        #     return redirect('mechlogin')  # Adjust the URL name to match your configuration

        # Save mechanic details
        Mechanics.objects.create(
            Name=name,
            Age=age,
            Address=address,
            Mobile=mob,
            Vehicle=veh,
            Place=pl,
            Latitude=lat,
            Longitude=long,
            Picture=pic,
            Username=uname,
            Email=email,
            Password=pw,
            Type="pending"
        )
        messages.success(request, "Registration successful. Awaiting approval.")
        return redirect('mechlogin')  # Adjust the URL name to match your configuration

    return redirect(mechlogin)


def mech_edit(req, mid):
    data = Mechanics.objects.get(Mechid=mid)
    return render(req, "Mechanic/edit_profile.html", {"data": data})


def view_profile_mech(request):
    mid = request.session.get('Mechid')
    data = Mechanics.objects.get(Mechid=mid)
    return render(request, "Mechanic/view_profile.html", {"data": data})


def mech_update(request, mid):
    if request.method == "POST":
        name = request.POST.get("name")
        age = request.POST.get("age")
        address = request.POST.get("Address")
        mob = request.POST.get("mobile")
        veh = request.POST.get("veh")
        pl = request.POST.get("place")
        lat = request.POST.get("lat")
        long = request.POST.get("long")
        uname = request.POST.get("uname")
        email = request.POST.get("email")
        pw = request.POST.get("password")
        latitude, longitude = get_coordinates_from_address(address)
        if latitude is not None and longitude is not None:
            print("Latitude:", latitude)
            print("Longitude:", longitude)
        else:
            print("Location not found.")
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((latitude, longitude), language='en')
        print(location)

        # Checking if location found or not
        # geolocator = Nominatim(user_agent="geoapiExercises")
        # location = geolocator.geocode(address)
        # if location:
        #     print(location.latitude, location.longitude)
        try:
            pic = request.FILES['pic']
            fs = FileSystemStorage()
            pic = fs.save(pic.name, pic)
        except MultiValueDictKeyError:
            pic = Mechanics.objects.get(Mechid=mid).Picture
        Mechanics.objects.filter(Mechid=mid).update(Name=name, Age=age, Address=address, Mobile=mob, Vehicle=veh,
                                                    Place=pl,
                                                    Latitude=latitude, Longitude=longitude, Picture=pic, Username=uname,
                                                    Email=email,
                                                    Password=pw)
        return redirect(view_profile_mech)


def get_address_by_location(latitude, longitude, language="en"):
    """This function returns an address as raw from a location
        will repeat until success"""
    # build coordinates string to pass to reverse() function
    coordinates = f"{latitude}, {longitude}"
    # sleep for a second to respect Usage Policy
    time.sleep(1)
    try:
        return app.reverse(coordinates, language=language).raw
    except:
        return get_address_by_location(latitude, longitude)


def service_register(req):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
    geolocator = Nominatim(user_agent="Webapp")
    location = geolocator.reverse((latitude, longitude), language='en')
    print(location.address)
    return render(req, "service_center/service_register.html", {'lati': latitude, 'longi': longitude})


from geopy.geocoders import Nominatim


def get_lat_long_from_pincode(pincode):
    geolocator = Nominatim(user_agent="my_app")  # Replace with your user agent name
    location = geolocator.geocode(query={'postalcode': pincode, 'country': 'IN'}, addressdetails=True)

    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None, None


def service_reg(request):
    if request.method == "POST":
        name = request.POST.get("bname")
        cname = request.POST.get("cname")
        age = request.POST.get("age")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin = request.POST.get("pin")
        mob = request.POST.get("mobile")
        pl = request.POST.get("place")
        lat = request.POST.get("lat")
        long = request.POST.get("long")
        pic = request.FILES['pic']
        des = request.POST.get("Description")
        hour = request.POST.get("hour")
        uname = request.POST.get("uname")
        email = request.POST.get("email")
        pw = request.POST.get("password")
        latitude, longitude = get_lat_long_from_pincode(pin)

        if latitude and longitude:
            print(f"Latitude: {latitude}, Longitude: {longitude}")
        else:
            print("Location not found for the provided pincode.")
        # if address:
        #     geolocator = Nominatim(user_agent="my_application")
        #     location = geolocator.geocode(address)
        #     if location:
        #         latitude = location.latitude
        #         longitude = location.longitude
        #         print(latitude)
        #         return JsonResponse({'latitude': latitude, 'longitude': longitude})
        #     else:
        #         return JsonResponse({'error': 'Address not found'}, status=400)
        # return JsonResponse({'error': 'Invalid request'}, status=400)

        ServiceCenter(BName=name, CPerson=cname, Age=age, Address=address, City=city, State=state, Hours=hour,
                      Mobile=mob, PIN=pin, Latitude=lat, Longitude=long,
                      Picture=pic, Username=uname, Email=email, Description=des, Password=pw, Type="pending").save()
        logintable(Username=uname, Password=pw, Type="pending")
        return redirect(service_login)


def service_edit(request, sid):
    data = ServiceCenter.objects.get(id=sid)
    return render(request, "service_center/edit_data.html", {"data": data})


def view_profile_service(request):
    sid = request.session.get('Serviceid')
    data = ServiceCenter.objects.get(id=sid)
    return render(request, "service_center/view_pro.html", {"data": data})


def service_update(request, sid):
    if request.method == "POST":
        name = request.POST.get("bname")
        cname = request.POST.get("cname")
        age = request.POST.get("age")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin = request.POST.get("pin")
        mob = request.POST.get("mobile")
        pl = request.POST.get("place")
        lat = request.POST.get("lat")
        long = request.POST.get("long")
        des = request.POST.get("Description")
        hour = request.POST.get("hour")
        uname = request.POST.get("uname")
        email = request.POST.get("email")
        pw = request.POST.get("password")
        coordinates = get_current_gps_coordinates()
        if coordinates is not None:
            latitude, longitude = coordinates
            print(f"Your current GPS coordinates are:")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
        else:
            print("Unable to retrieve your GPS coordinates.")
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((latitude, longitude), language='en')
        print(location)
        try:
            pic = request.FILES['pic']
            fs = FileSystemStorage()
            pic = fs.save(pic.name, pic)
        except MultiValueDictKeyError:
            pic = ServiceCenter.objects.get(id=sid).Picture
        ServiceCenter.objects.filter(id=sid).update(BName=name, CPerson=cname, Age=age, Address=address, City=city,
                                                    State=state, Hours=hour,
                                                    Mobile=mob, PIN=pin, Latitude=latitude, Longitude=longitude,
                                                    Picture=pic, Username=uname, Description=des, Email=email,
                                                    Password=pw)
        return redirect(view_profile_service)


def get_lat_lng_from_address(request):
    if request.method == 'GET':
        address = request.GET.get('address')
        if address:
            geolocator = Nominatim(user_agent="my_application")
            location = geolocator.geocode(address)
            if location:
                latitude = location.latitude
                longitude = location.longitude
                return JsonResponse({'latitude': latitude, 'longitude': longitude})
            else:
                return JsonResponse({'error': 'Address not found'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


# user-----------------------
def searchmech(req):
    vehicle = req.GET.get("veh")
    latitude = req.GET.get("lat")
    longitude = req.GET.get("long")
    print(latitude)
    data = Mechanics.objects.filter(Latitude=latitude).values() & Mechanics.objects.filter(
        Vehicle=vehicle).values() & Mechanics.objects.filter(Longitude=longitude).values()
    print(data)
    return render(req, "User_Pages/viewmech.html", {"data": data})


def mechlogin(req):
    return render(req, "Mechanic/signin.html")


def login_mech(request):
    if request.method == "POST":
        un = (request.POST.get("name"))
        pw = (request.POST.get("password"))

        data = Mechanics.objects.filter(Username=un, Password=pw, Type="Mechanics").values()
        print(data)
        if data.exists():
            mid = data[0]['Mechid']
            token = generate_token(mid, 'mechanic')  # Generate a token for the user
            print(token)  # Optional: Print the token for debugging purposes
            print(mid)
            request.session['Mechname'] = un
            request.session['MPassword'] = pw
            request.session['Mechid'] = mid
            messages.success(request, "Login success")
            # return render(request, "indexuser.html", {'user_type': user_type})
            return redirect(mech_home)
        else:
            messages.warning(request, "Invalid user or Password")
            return redirect(mechlogin)
    else:
        messages.warning(request, "User_Pages not found")
        return redirect(mechlogin)


def mechlogout(request):
    del request.session['Mechname']
    del request.session['MPassword']
    del request.session['Mechid']
    messages.success(request, "Logout success")
    return redirect(indexpage)


def add_service(request):
    data = Service.objects.filter(username=request.session['Username'])
    return render(request, "Mechanic/services.html", {'data': data})


def save_service(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        service = request.POST.get("service")
        price = request.POST.get("price")
        Service(username=username, service=service, price=price).save()
        return redirect(add_service)


def delete_service(req, sid):
    Service.objects.filter(id=sid).delete()
    return redirect(add_service)


def mech_home(req):
    mechanic_id = req.session.get('Mechid')
    data = feedback.objects.all()
    print(data)
    return render(req, "Mechanic/mech_index.html", {"mechanic_id": mechanic_id, "data": data})


import heapq


def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return distances


def find_nearest_location(graph, start):
    distances = dijkstra(graph, start)
    nearest_location = min(distances, key=distances.get)
    return nearest_location, distances[nearest_location]


def searchservicecenter(req):
    place = req.GET.get("place")
    # latitude = req.GET.get("lat")
    # longitude = req.GET.get("long")
    data = ServiceCenter.objects.filter(Address=place)

    print(data)
    return render(req, "User_Pages/view_service.html", {"data": data})


from haversine import haversine, Unit


def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate the distance between two points in kilometers
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)


def search_nearest_locations_mech(request):
    if request.method == 'GET':
        coordinates = get_current_gps_coordinates()
        if coordinates is not None:
            latitude, longitude = coordinates
            print(f"Your current GPS coordinates are:")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
        else:
            print("Unable to retrieve your GPS coordinates.")
        # latitude = float(request.GET.get('latitude'))
        # longitude = float(request.GET.get('longitude'))
        if latitude is not None and longitude is not None:
            # Fetch all locations from the database
            locations = Mechanics.objects.all()
            # Calculate distances for each location and sort by distance
            nearest_locations = sorted(locations,
                                       key=lambda loc: calculate_distance(latitude, longitude, float(loc.Latitude),
                                                                          float(loc.Longitude)))
            # Serialize nearest locations as JSON
            response_data = [{'idd': loc.Mechid, 'name': loc.Name, 'latitude': loc.Latitude, 'longitude': loc.Longitude,
                              'pic': loc.Picture, 'address': loc.Address} for loc in nearest_locations]
            print(response_data)
            return render(request, "User_Pages/viewmech.html", {"data": response_data})
            # return JsonResponse(response_data, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def send_feedback(request):
    return render(request, "User_Pages/send_feedback.html")


def sendfeedback_post(request):
    if request.method == "POST":
        name = request.POST.get("name")
        msg = request.POST.get("message")
        feedback(name=name, message=msg).save()
        return redirect(indexpage)


def how_it_works(request):
    data = feedback.objects.all()
    return render(request, "how_it_works.html", {"data": data})


def service_login(req):
    return render(req, "service_center/service_signin.html")


def login_service(request):
    if request.method == "POST":
        un = request.POST.get("name")
        pw = request.POST.get("pwd")
        data = ServiceCenter.objects.filter(Username=un, Password=pw, Type="service").values()
        print(data)
        if data.exists():
            sid = data[0]['id']
            print(sid)
            request.session['Servicename'] = un
            request.session['SPassword'] = pw
            request.session['Serviceid'] = sid
            messages.success(request, "Login success")
            # return render(request, "indexuser.html", {'user_type': user_type})
            return redirect(service_home)
        else:
            messages.warning(request, "Invalid user or Password")
            return redirect(service_login)
    else:
        messages.warning(request, "User_Pages not found")
        return redirect(service_login)


def service_home(req):
    return render(req, "service_center/service_index.html")


def service_password(request, sid):
    if request.method == "POST":
        uname = request.POST.get("username")
        pwd = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        if pwd == cpwd:
            ServiceCenter.objects.filter(id=sid).update(Password=pwd)
    return redirect(service_login)


def userlogin(req):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
    geolocator = Nominatim(user_agent="Webapp")
    location = geolocator.reverse((latitude, longitude), language='en')
    print(location.address)
    return render(req, "User_Pages/register.html", {'lat': latitude, 'long': longitude, 'loc': location})


def loginuser(request):
    return render(request, "User_Pages/loginuser.html")


def check_login(request):
    if request.session.get('_auth_user_id'):
        # User_Pages is logged in
        logged_in = True
    else:
        # User_Pages is not logged in
        logged_in = False

    return JsonResponse({'logged_in': logged_in})


def save_userlogin(request):
    if request.method == "POST":
        un = request.POST.get("uname")
        pwd = request.POST.get("password")
        data = userdatas.objects.filter(Mobile=un, Password=pwd).values()
        print(data)

        if data.exists():
            name = data[0]['Name']
            Mob = data[0]['Mobile']
            Uid = data[0]['Userid']
            token = generate_token(Uid, 'user')  # Generate a token for the user
            print(token)
            print(Uid)
            request.session['Username'] = name
            request.session['Mobile'] = Mob
            request.session['Password'] = pwd
            request.session['Userid'] = Uid
            messages.success(request, "Login success")
            return redirect(indexpage)
        else:
            messages.warning(request, "Invalid user or Password")
            return redirect(loginuser)
    else:
        messages.warning(request, "User_Pages not found")
        return redirect(loginuser)


def userlogout(request):
    del request.session['Username']
    del request.session['Password']
    del request.session['Userid']
    del request.session['Mobile']
    messages.success(request, "Logout success")
    return redirect(indexpage)


def servicelogout(request):
    del request.session['Servicename']
    del request.session['SPassword']
    del request.session['Serviceid']
    messages.success(request, "Logout success")
    return redirect(indexpage)


def save_userdata(req):
    if req.method == "POST":
        name = req.POST.get("name")
        email = req.POST.get("email")
        mobile = req.POST.get("mobile")
        latitude = req.POST.get("lat")
        longitude = req.POST.get("long")
        location = req.POST.get("loc")
        password = req.POST.get("password")
        cp = req.POST.get("cpassword")
        req.session['Username'] = name
        if userdatas.objects.filter(Mobile=mobile).exists():
            messages.warning(req, "Mobile number already exists.")
            return redirect('userlogin')  # Adjust URL name as needed

            # Check if passwords match
        if password != cp:
            messages.warning(req, "Passwords do not match.")
            return redirect('userlogin')  # Adjust URL name as needed

            # Save user data if no errors
        userdatas.objects.create(
            Name=name,
            Email=email,
            Mobile=mobile,
            Latitude=latitude,
            Longitude=longitude,
            Location=location,
            Password=password,  # Note: Consider using hashed passwords for security
            Cpassword=cp  # Note: You typically don’t store the confirm password
        )

        messages.success(req, "User data saved successfully.")
        return redirect(loginuser)  # Adjust URL name as needed

        # Handle GET requests or other methods if needed
    return redirect(userlogin)  # Adjust URL name as needed
    # userdatas(Name=name, Email=email, Mobile=mobile, Latitude=latitude, Longitude=longitude, Location=location,
    #           Password=password, Cpassword=cp).save()
    # # User(name=name,phone=mobile,password=password).save()
    # return redirect(userlogin)




def send_request(request):
    if request.method == "POST":
        description = request.POST.get("des")
        coordinates = get_current_gps_coordinates()
        if coordinates is not None:
            latitude, longitude = coordinates
            print(f"Your current GPS coordinates are:")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
        else:
            print("Unable to retrieve your GPS coordinates.")
        geolocator = Nominatim(user_agent="Webapp")
        location = geolocator.reverse((latitude, longitude), language='en')
        print(location.address)
        # mid=request.POST.get("mid")
        uid = request.session.get('Userid')
        # geolocator = Nominatim(user_agent="pin_locator")
        # location = geolocator.reverse((latitude, longitude), exactly_one=True)
        try:
            pin_location = PINLocation.objects.get(latitude=latitude, longitude=longitude)
            pin_code = pin_location.pin_code
            print(pin_code)
            # return render(request, 'pin_finder/result.html', {'pin_code': pin_code})
        except PINLocation.DoesNotExist:
            print("pincode not found")
            # return render(request, 'pin_finder/result.html', {'pin_code': 'PIN code not found'})

        if location:
            address = location.raw['address']
            pin_code = address.get('postcode', 'PIN code not found')
            print(pin_code)
        if uid is not None:
            try:
                # Retrieve userdatas instance using uid
                user_data = userdatas.objects.get(Userid=uid)

                # Assuming other fields like Mechid, latitude, longitude, status are also passed
                mid = request.POST.get("mid")
                # latitude = request.POST.get("latitude")
                # longitude = request.POST.get("longitude")

                # Retrieve Mechanics instance using mid
                mechanic_instance = Mechanics.objects.get(Mechid=mid)

                # Create UserRequests instance
                a = UserRequests.objects.create(
                    Userid=user_data,
                    Mechid=mechanic_instance,
                    latitude=latitude,
                    longitude=longitude,
                    status="Pending",
                    description=description
                )
                a.save()
                messages.success(request, "Request sent successfully")
                send_notification(request, mechanic_id=mid)
                return redirect(search_nearest_locations)

            except userdatas.DoesNotExist:
                messages.warning(request, "User data does not exist.")
                return redirect(loginuser)

            except Mechanics.DoesNotExist:
                messages.error(request, "Mechanic with provided ID does not exist.")
                return redirect(search_nearest_locations)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect(search_nearest_locations)

        else:
            messages.warning(request, "User not logged in.")
            return redirect(loginuser)

        # mechanic_phone_number = '+918281984271'  # Replace with actual mechanic's phone number
        # sms_body = 'New request received from a user.'  # Customize message as needed
        # send_sms(mechanic_phone_number, sms_body)
        # print(uid)


def book_mechanic(request):
    if request.method == "POST":
        description = request.POST.get("des")
        mid = request.POST.get("mid")
        uid = request.session.get('Userid')

        if uid is not None:
            try:
                # Retrieve userdatas instance using uid
                user_data = userdatas.objects.get(Userid=uid)

                # Retrieve Mechanics instance using mid
                mechanic_instance = Mechanics.objects.get(Mechid=mid)

                # Create UserRequests instance
                request_instance = UserRequests(
                    Userid=user_data,
                    Mechid=mechanic_instance,
                    status="Pending",
                    description=description
                )
                request_instance.save()

                messages.success(request, "Request sent successfully")
                # Optionally send notification here
                return redirect('search_nearest_locations')

            except userdatas.DoesNotExist:
                messages.warning(request, "User data does not exist.")
                return redirect('loginuser')

            except Mechanics.DoesNotExist:
                messages.error(request, "Mechanic with provided ID does not exist.")
                return redirect('search_nearest_locations')

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('search_nearest_locations')

        else:
            messages.warning(request, "User not logged in.")
            return redirect('loginuser')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('search_nearest_locations')


def book_mech(request):
    if request.method == 'POST':
        center_id = request.POST.get('center_id')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        uid = request.session.get('Userid')
        print(uid)
        # Validate and process the booking (example)
        if uid is not None:
            try:
                # Create a Booking object

                booking = Booking.objects.create(
                    user_id=uid,
                    service_center_id=center_id,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    status='pending'
                )

                # Optionally, you can perform additional actions here, such as sending notifications

                return redirect(search_nearest_locations_service)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            messages.warning(request, "Register/Login First")
            return redirect(loginuser)
    return JsonResponse({'error': 'Invalid request'}, status=400)


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


# def notify_mechanic(request, mechanic_id):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f'mechanic_{mechanic_id}',
#         {
#             'type': 'mechanic_message',
#             'message': 'New assistance request received!'
#         }
#     )
#     return render(request, 'mechanic/get_notify.html')
#
# from django.shortcuts import render
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer

@csrf_exempt  # For demo purposes; use CSRF protection as needed
def notify_mechanic(request):
    if request.method == 'POST':
        try:
            mechanic_id = request.POST.get('mechanic_id')
            print(mechanic_id)
            if mechanic_id:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'mechanic_{mechanic_id}',
                    {
                        'type': 'mechanic_message',
                        'message': 'New assistance request received!'
                    }
                )
                print(f"Notification sent to mechanic {mechanic_id}")
                return HttpResponse(status=200)
            else:
                print("Mechanic ID not found in POST data")
                return HttpResponse(status=400)  # Bad request if mechanic_id is missing
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return HttpResponse(status=500)  # Internal server error
    else:
        return HttpResponse(status=405)  # Method not allowed for non-POST requests


def view_details(request, mid):
    data = Mechanics.objects.get(Mechid=mid)
    return render(request, "User_Pages/view_mech_single.html", {"data": data})


def search_nearest_locations(request):
    if request.method == 'GET':
        # Mocking coordinates for testing purposes, replace with actual retrieval
        userId = request.session.get('Userid')
        coordinates = get_current_gps_coordinates()
        if coordinates is not None:
            latitude, longitude = coordinates
            print(f"Your current GPS coordinates are:")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")

            # Fetch all locations from the database
            locations = Mechanics.objects.filter(Type='Mechanics')

            # Filter locations within 5 km radius
            nearest_locations = []
            for loc in locations:
                dist = calculate_distance(latitude, longitude, float(loc.Latitude), float(loc.Longitude))
                if dist <= 5.0:  # Adjust distance threshold as needed
                    nearest_locations.append({
                        'id': loc.Mechid,
                        'name': loc.Name,
                        'latitude': loc.Latitude,
                        'longitude': loc.Longitude,
                        'picture': loc.Picture,
                        'address': loc.Address,
                        'mobile': loc.Mobile,
                        'vehicle': loc.Vehicle,
                        'distance': dist  # Optionally include distance in response
                    })

            if nearest_locations:
                # Render data to a template for display
                return render(request, "User_Pages/viewmech.html", {"data": nearest_locations, 'userId': userId})
            else:
                messages.warning(request, "No mechanics found in this area.")
                return redirect('indexpage')  # Use URL name for redirection

        else:
            messages.warning(request, "Unable to retrieve GPS coordinates.")
            return redirect('indexpage')  # Use URL name for redirection

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def request_status(request):
    coordinates = get_current_gps_coordinates()

    if coordinates is None:
        print("Unable to retrieve your GPS coordinates.")
        # Handle the case where GPS coordinates are not available
        user_latitude, user_longitude = None, None
    else:
        user_latitude, user_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {user_latitude}")
        print(f"Longitude: {user_longitude}")

    geolocator = Nominatim(user_agent="location_app")

    if user_latitude is not None and user_longitude is not None:
        location = geolocator.reverse((user_latitude, user_longitude), language='en')
        print(location)
    else:
        location = "No location data available"

    uid = request.session.get('Userid')
    print(uid)

    if uid:
        mechanic_requests = UserRequests.objects.filter(Userid=uid).order_by('-timestamp')
    else:
        mechanic_requests = []

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Mechid
        reqid = req.id
        user_id = user_data.Mechid
        username = user_data.Name
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        # mechid=req.Mechid
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments[0].status if mech_payments.exists() else None

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status,
            'uid': uid
        })
        print(user_data)
        # mechanic_id = request.user.mechanic.id if hasattr(request.user, 'mechanic') else None
        # print(mechanic_id)
        # Only create the map once, using the first request's location

        if user_map is None and latitude is not None and longitude is not None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)
            folium.Marker([user_latitude, user_longitude], tooltip=f'User: {username}, Status: {status}').add_to(
                user_map)
            folium.Marker([latitude, longitude], tooltip='Mechanic Location').add_to(user_map)

            # Add routing between mechanic's location and user's location
            first_request_location = [latitude, longitude]
            folium.PolyLine(locations=[(user_latitude, user_longitude), first_request_location],
                            color='blue', weight=2.5, opacity=1).add_to(user_map)

        # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,
    }

    return render(request, "User_Pages/Request_status.html", context)
    # else:
    #     messages.warning(request,"No mechaics found")
    #     return redirect(indexpage)


def request_status_accepted(request):
    coordinates = get_current_gps_coordinates()

    if coordinates is None:
        print("Unable to retrieve your GPS coordinates.")
        # Handle the case where GPS coordinates are not available
        user_latitude, user_longitude = None, None
    else:
        user_latitude, user_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {user_latitude}")
        print(f"Longitude: {user_longitude}")

    geolocator = Nominatim(user_agent="location_app")

    if user_latitude is not None and user_longitude is not None:
        location = geolocator.reverse((user_latitude, user_longitude), language='en')
        print(location)
    else:
        location = "No location data available"

    uid = request.session.get('Userid')
    print(uid)

    if uid:
        mechanic_requests = UserRequests.objects.filter(Userid=uid, status='Accepted').order_by('-timestamp')
    else:
        mechanic_requests = []

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Mechid
        reqid = req.id
        user_id = user_data.Mechid
        username = user_data.Name
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        # mechid=req.Mechid
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments[0].status if mech_payments.exists() else None

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status,
            'uid': uid
        })
        print(user_data)
        # mechanic_id = request.user.mechanic.id if hasattr(request.user, 'mechanic') else None
        # print(mechanic_id)
        # Only create the map once, using the first request's location

        if user_map is None and latitude is not None and longitude is not None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)
            folium.Marker([user_latitude, user_longitude], tooltip=f'User: {username}, Status: {status}').add_to(
                user_map)
            folium.Marker([latitude, longitude], tooltip='Mechanic Location').add_to(user_map)

            # Add routing between mechanic's location and user's location
            first_request_location = [latitude, longitude]
            folium.PolyLine(locations=[(user_latitude, user_longitude), first_request_location],
                            color='blue', weight=2.5, opacity=1).add_to(user_map)

        # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,
    }

    return render(request, "User_Pages/Request_status.html", context)
    # else:
    #     messages.warning(request,"No mechaics found")
    #     return redirect(indexpage)


def mapview_user(request):
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        user_latitude, user_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {user_latitude}")
        print(f"Longitude: {user_longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")
        user_latitude, user_longitude = None, None

    # Reverse geocoding to get location details
    location = None
    if user_latitude is not None and user_longitude is not None:
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((user_latitude, user_longitude), language='en')
        print(location)

    # Retrieve mechanic's requests
    uid = request.session.get('Userid')
    print(uid)
    mechanic_requests = UserRequests.objects.filter(Userid=uid, status='Accepted').order_by('-timestamp')

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Mechid
        reqid = req.id
        user_id = user_data.Mechid
        username = user_data.Name
        # user_location = user_data.Location
        status = req.status
        latitude = user_data.Latitude
        longitude = user_data.Longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile
        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        if latitude is None or longitude is None:
            continue
        print(latitude, longitude)
        timestamp_str = format(timestamp, 'Y-m-d H:i:s')

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            # 'latitude': latitude,
            # 'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp_str,
            'payment_status': payment_status,
            'user_latitude': user_latitude,
            'user_longitude': user_longitude,
            'mechanic_latitude': latitude,
            'mechanic_longitude': longitude
        })

        # Only create the map once, using the first request's location
        if user_map is None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)

            # Add markers for user and mechanic locations
        folium.Marker(
            [latitude, longitude],
            tooltip=f'User: {username}, Status: {status}',
            icon=folium.Icon(color='blue', icon='user', prefix='fa')
        ).add_to(user_map)

        if user_latitude and user_longitude:
            folium.Marker(
                [user_latitude, user_longitude],
                tooltip='Mechanic Location',
                icon=folium.Icon(color='red', icon='wrench', prefix='fa')
            ).add_to(user_map)

            # Add routing between mechanic's location and user's location
            folium.PolyLine(
                locations=[(user_latitude, user_longitude), (latitude, longitude)],
                color='blue',
                weight=2.5,
                opacity=1
            ).add_to(user_map)
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"

    context = {
        'user_map': user_map,
        'data': json.dumps(data),

    }
    return render(request, "User_Pages/mapview.html", context)


def request_status_workdone(request):
    coordinates = get_current_gps_coordinates()

    if coordinates is None:
        print("Unable to retrieve your GPS coordinates.")
        # Handle the case where GPS coordinates are not available
        user_latitude, user_longitude = None, None
    else:
        user_latitude, user_longitude = coordinates
        print(f"Your current GPS coordinates are:")
        print(f"Latitude: {user_latitude}")
        print(f"Longitude: {user_longitude}")

    geolocator = Nominatim(user_agent="location_app")

    if user_latitude is not None and user_longitude is not None:
        location = geolocator.reverse((user_latitude, user_longitude), language='en')
        print(location)
    else:
        location = "No location data available"

    uid = request.session.get('Userid')
    print(uid)

    if uid:
        mechanic_requests = UserRequests.objects.filter(Userid=uid, status='Work done').order_by('-timestamp')
    else:
        mechanic_requests = []

    data = []
    user_map = None

    for req in mechanic_requests:
        user_data = req.Mechid
        reqid = req.id
        user_id = user_data.Mechid
        username = user_data.Name
        status = req.status
        latitude = req.latitude
        longitude = req.longitude
        timestamp = req.timestamp
        Mobile = user_data.Mobile

        mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        if mech_payments.exists():
            # Since mech_payments is a queryset, you need to iterate or access a specific instance
            # Assuming you want the amount from the first Mechpayment (you can adjust as needed)
            first_payment = mech_payments.first()
            amount = first_payment.Amount  # Accessing the Amount field of the first Mechpayment
            payment_status = first_payment.status  # Accessing the status field of the first Mechpayment
        else:
            amount = None
            payment_status = None

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'latitude': latitude,
            'longitude': longitude,
            'Mobile': Mobile,
            'status': status,
            'timestamp': timestamp,
            'payment_status': payment_status,
            'amount': amount
        })

        # Only create the map once, using the first request's location
        if user_map is None and latitude is not None and longitude is not None:
            user_map = folium.Map(location=[latitude, longitude], zoom_start=13)
            folium.Marker([user_latitude, user_longitude], tooltip=f'User: {username}, Status: {status}').add_to(
                user_map)
            folium.Marker([latitude, longitude], tooltip='Mechanic Location').add_to(user_map)

            # Add routing between mechanic's location and user's location
            first_request_location = [latitude, longitude]
            folium.PolyLine(locations=[(user_latitude, user_longitude), first_request_location],
                            color='blue', weight=2.5, opacity=1).add_to(user_map)

    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,
    }

    return render(request, "User_Pages/request_workdone.html", context)


def payment_mech(request):
    if request.method == "POST":
        un = request.POST.get("un")
        email = request.POST.get("email")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        msg = request.POST.get("bill")
        total = request.POST.get("total")
        Order(uname=un, Email=email, Phone=phone, Address=address, Message=msg, Totalprice=total).save()
        return redirect(payment_page)


def payment_page_mech(req, rid):
    data = Mechpayment.objects.filter(Reqid=rid)
    print(data)
    # uid=data['Userid']
    Mechpayment.objects.filter(Reqid=rid).update(status='paid')
    if data.exists():
        # Since data is a queryset, you need to iterate or access a specific instance
        # Assuming you want the amount from the first Mechpayment (you can adjust as needed)
        first_payment = data.first()
        pay = first_payment.Amount  # Accessing the Amount field of the first Mechpayment
        print(pay)  # Output the amount to console or process further
        amount = int(pay * 100)
        pay_str = str(amount)
    else:
        print("No Mechpayment found with Reqid =", rid)
    # pay = data.Amount

    for i in pay_str:
        print(i)
    if req.method == "POST":
        order_currency = "INR"
        client = razorpay.Client(auth=('rzp_test_CagytDuj1DwsMy', 'jMzxj0rpJ7T0ldH7zQi904Zb'))
        payment = client.order.create({'amount': amount, 'currency': order_currency, 'payment_capture': '1'})
    return render(req, "User_Pages/paymentmech.html", {'customer': data, 'pay_str': pay_str})


def amount_mech(request):
    if request.method == 'POST':
        center_id = request.POST.get('center_id')
        amount = request.POST.get('amount')
        booking_time = request.POST.get('booking_time')

        # Retrieve the ServiceCenter object
        try:
            service_center = ServiceCenter.objects.get(id=center_id)
        except ServiceCenter.DoesNotExist:
            return JsonResponse({'error': 'Service center not found'}, status=404)

        # Create a Booking object
        booking = Booking(service_center=service_center,
                          booking_time=booking_time, status='pending')
        booking.save()

        # Optionally, you can perform additional actions here, such as sending notifications

        return JsonResponse({'success': 'Booking successful!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def book_service(request, pid):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # uid=request.session.get('Userid')
        # print(uid)
        # Validate and process the booking (example)
        # if uid is not None:
        #     try:
        # Create a Booking object

        Mechpayment.objects.filter(id=pid).update(Amount=amount)

        # Optionally, you can perform additional actions here, such as sending notifications

        return redirect(view_workdone_request)

# ........................SERVICE CENTER....................
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance (in kilometers) between two points on the Earth's surface using Haversine formula.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    earth_radius = 6371  # Radius of the Earth in kilometers
    distance = earth_radius * c

    return distance


def search_nearest_locations_service(request):
    if request.method == 'GET':
        # Mocking coordinates for testing purposes, replace with actual retrieval
        coordinates = get_current_gps_coordinates()
        if coordinates is not None:
            latitude, longitude = coordinates
            print(f"Your current GPS coordinates are:")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")

            # Fetch all locations from the database
            locations = ServiceCenter.objects.all()

            # Filter locations within 5 km radius
            nearest_locations = []
            for loc in locations:
                dist = calculate_distance(latitude, longitude, float(loc.Latitude), float(loc.Longitude))
                if dist <= 200.0:  # Adjust distance threshold as needed
                    nearest_locations.append({
                        'id': loc.id,
                        'name': loc.BName,
                        'latitude': loc.Latitude,
                        'longitude': loc.Longitude,
                        'picture': loc.Picture,
                        'address': loc.Address,
                        'description': loc.Description,
                        'Hours': loc.Hours,
                        'distance': dist  # Optionally include distance in response
                    })

            print(nearest_locations)
            from datetime import date

            today = date.today()

            # Render data to a template for display
            return render(request, "User_Pages/view_service.html", {"data": nearest_locations, "today": today})

            # If you want to return JSON response instead
            # return JsonResponse(nearest_locations, safe=False)

        else:
            print("Unable to retrieve your GPS coordinates.")
            return JsonResponse({'error': 'Unable to retrieve GPS coordinates.'}, status=400)

    # Handle invalid requests
    return JsonResponse({'error': 'Invalid request'}, status=400)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking
from datetime import datetime


def book_service_center(request):
    if request.method == 'POST':
        center_id = request.POST.get('center_id')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')

        # Retrieve the ServiceCenter object
        try:
            service_center = ServiceCenter.objects.get(id=center_id)
        except ServiceCenter.DoesNotExist:
            return JsonResponse({'error': 'Service center not found'}, status=404)

        # Create a Booking object
        booking = Booking(service_center=service_center,
                          booking_date=booking_date,
                          booking_time=booking_time, status='pending')
        booking.save()

        # Optionally, you can perform additional actions here, such as sending notifications

        return JsonResponse({'success': 'Booking successful!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def book_service(request):
    if request.method == 'POST':
        center_id = request.POST.get('center_id')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        uid = request.session.get('Userid')
        print(uid)
        # Validate and process the booking (example)
        if uid is not None:
            try:
                # Create a Booking object

                booking = Booking.objects.create(
                    user_id=uid,
                    service_center_id=center_id,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    status='pending'
                )

                # Optionally, you can perform additional actions here, such as sending notifications

                return redirect(search_nearest_locations_service)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            messages.warning(request, "Register/Login First")
            return redirect(loginuser)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def service_details(request, sid):
    data = ServiceCenter.objects.get(id=sid)
    return render(request, "User_Pages/service_single.html", {"data": data})


def view_booking_status(request):
    sid = request.session.get('Userid')
    print(sid)
    user_booking = Booking.objects.filter(user_id=sid).order_by('-date_booked')
    print(user_booking)
    data = []
    user_map = None

    for req in user_booking:
        user_data = req.service_center
        print(user_data)
        reqid = req.id
        user_id = user_data.id
        username = user_data.BName
        cname = user_data.CPerson
        latitude = user_data.Latitude
        longitude = user_data.Longitude
        status = req.status
        date = req.date_booked
        btime = req.booking_time
        bdate = req.booking_date
        Mobile = user_data.Mobile

        # mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        # payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        # if latitude is None or longitude is None:
        #     continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'date': date,
            'btime': btime,
            'Mobile': Mobile,
            'status': status,
            'bdate': bdate,
            'cname': cname,
            'latitude': latitude,
            'longitude': longitude,

            # 'payment_status': payment_status
        })



    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,

    }

    print(context)

    return render(request, "User_Pages/view_booking_status.html", context)


def view_booking(request):
    sid = request.session.get('Serviceid')
    print(sid)
    user_booking = Booking.objects.filter(service_center_id=sid, status='pending')
    print(user_booking)
    data = []
    user_map = None

    for req in user_booking:
        user_data = req.user
        print(user_data)
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        email = user_data.Email
        user_location = user_data.Location
        status = req.status
        date = req.date_booked
        btime = req.booking_time
        bdate = req.booking_date
        Mobile = user_data.Mobile
        # mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        # payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        # if latitude is None or longitude is None:
        #     continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'date': date,
            'btime': btime,
            'Mobile': Mobile,
            'email': email,
            'status': status,
            'bdate': bdate,
            # 'payment_status': payment_status
        })



    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,

    }

    print(context)
    sms_gateway = {
        'AT&T': '@txt.att.net',
        'Verizon': '@vtext.com',
        'T-Mobile': '@tmomail.net',
        'Sprint': '@messaging.sprintpcs.com',
        # Add more carriers and their respective gateways as needed
    }
    recipient_carrier = 'Verizon'
    Mobile = '813980821'
    message = 'Request accepted successfully'
    # Check if recipient's carrier is supported
    if recipient_carrier in sms_gateway:
        gateway_address = str(Mobile) + sms_gateway[recipient_carrier]
    else:
        print(f'Carrier {recipient_carrier} is not supported for SMS sending.')
        return

    # Construct the email message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = ''  # Subject will be part of the SMS content
    msg['From'] = 'your_email@example.com'  # Your email address

    # Replace with your SMTP server details
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    smtp_username = 'your_email@example.com'
    smtp_password = 'your_email_password'

    try:
        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg, from_addr=smtp_username, to_addrs=gateway_address)

        print(f'SMS sent successfully to {Mobile}')
    except Exception as e:
        print(f'Failed to send SMS to {Mobile}. Error: {e}')

    # Example usage
    recipient_number = '5551234567'  # User's phone number
    message_content = 'Your booking has been accepted for July 16, 2024. Thank you!'
    recipient_carrier = 'Verizon'  # Replace with actual recipient's carrier

    return render(request, "service_center/view_booking.html", context)


def accept_booking(request, bid):
    booking = Booking.objects.filter(id=bid).first()

    if booking:
        # Update the booking status
        booking.status = 'accepted'
        booking.save()

        # Check the booking status
        if booking.status == 'accepted':  # Adjust to match your actual status
            subject = 'Booking Confirmation'
            html_message = render_to_string('service_center/booking_confirmation.html',
                                            {'order': booking, 'user': booking.user})
            plain_message = strip_tags(html_message)
            from_email = 'getmehelp73@gmail.com'
            to_email = booking.user.Email  # Adjust this if your email field is different

            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    # Redirect to a specific view or URL
    return redirect('view_booking')


def reject_booking(request, bid):
    Booking.objects.filter(id=bid).update(status='rejeted')
    return redirect(view_booking)


import smtplib
from email.message import EmailMessage


# Function to send SMS via email-to-SMS gateway
def send_sms_via_email(recipient_number, message, recipient_carrier):
    # Define email-to-SMS gateways for carriers
    sms_gateway = {
        'AT&T': '@txt.att.net',
        'Verizon': '@vtext.com',
        'T-Mobile': '@tmomail.net',
        'Sprint': '@messaging.sprintpcs.com',
        # Add more carriers and their respective gateways as needed
    }

    # Check if recipient's carrier is supported
    if recipient_carrier in sms_gateway:
        gateway_address = recipient_number + sms_gateway[recipient_carrier]
    else:
        print(f'Carrier {recipient_carrier} is not supported for SMS sending.')
        return

    # Construct the email message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = ''  # Subject will be part of the SMS content
    msg['From'] = 'your_email@example.com'  # Your email address

    # Replace with your SMTP server details
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    smtp_username = 'your_email@example.com'
    smtp_password = 'your_email_password'

    try:
        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg, from_addr=smtp_username, to_addrs=gateway_address)

        print(f'SMS sent successfully to {recipient_number}')
    except Exception as e:
        print(f'Failed to send SMS to {recipient_number}. Error: {e}')


# Example usage
recipient_number = '5551234567'  # User's phone number
message_content = 'Your booking has been accepted for July 16, 2024. Thank you!'
recipient_carrier = 'Verizon'  # Replace with actual recipient's carrier

send_sms_via_email(recipient_number, message_content, recipient_carrier)


def view_accepted_booking(request):
    sid = request.session.get('Serviceid')
    print(sid)
    user_booking = Booking.objects.filter(service_center_id=sid, status='accepted')
    print(user_booking)
    data = []
    user_map = None

    for req in user_booking:
        user_data = req.user
        print(user_data)
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        date = req.date_booked
        btime = req.booking_time
        bdate = req.booking_date
        Mobile = user_data.Mobile
        # mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        # payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        # if latitude is None or longitude is None:
        #     continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'date': date,
            'btime': btime,
            'Mobile': Mobile,
            'status': status,
            'bdate': bdate,
            # 'payment_status': payment_status
        })



    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,

    }

    print(context)

    return render(request, "service_center/view_accepted_booking.html", context)


def reject_booking(request, bid):
    Booking.objects.filter(id=bid).update(status='rejected')
    return redirect(view_booking)


def view_rejected_booking(request):
    sid = request.session.get('Serviceid')
    print(sid)
    user_booking = Booking.objects.filter(service_center_id=sid, status='rejected')
    print(user_booking)
    data = []
    user_map = None

    for req in user_booking:
        user_data = req.user
        print(user_data)
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        user_location = user_data.Location
        status = req.status
        date = req.date_booked
        btime = req.booking_time
        bdate = req.booking_date
        Mobile = user_data.Mobile
        # mech_payments = Mechpayment.objects.filter(Reqid=reqid)
        # payment_status = mech_payments.first().status if mech_payments.exists() else None  # Skip entries with missing or invalid coordinates
        # if latitude is None or longitude is None:
        #     continue

        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'date': date,
            'btime': btime,
            'Mobile': Mobile,
            'status': status,
            'bdate': bdate,
            # 'payment_status': payment_status
        })


    # Render the map in HTML
    if user_map:
        user_map = user_map._repr_html_()
    else:
        user_map = "No location data available"
    context = {
        'user_map': user_map,
        'data': data,

    }

    print(context)

    return render(request, "service_center/view_rejected_booking.html", context)


def view_feedback(request):
    sid = request.session.get('Serviceid')
    print(sid)
    user_booking = servicefeedback.objects.filter(service_center_id=sid)
    print(user_booking)
    data = []
    for req in user_booking:
        user_data = req.user
        print(user_data)
        reqid = req.id
        user_id = user_data.Userid
        username = user_data.Name
        feed = req.feedback
        data.append({
            'userid': user_id,
            'reqid': reqid,
            'username': username,
            'feedback': feed
        })
    context = {
        'data': data
    }
    return render(request, "service_center/view_feedback.html", context)


# ...............Accessories................

def view_accessories(request):
    # data = Products.objects.all()
    # cat=Category.objects.all()
    category_id = request.POST.get('category')

    if category_id:
        data = Products.objects.filter(Category=category_id)
    else:
        data = Products.objects.all()

    categories = Category.objects.all()
    return render(request, "User_Pages/view_accessories.html", {"data": data, "cat": categories})


def view_accessories_mech(request):
    category_id = request.POST.get('category')

    if category_id:
        data = Products.objects.filter(Category=category_id)
    else:
        data = Products.objects.all()

    categories = Category.objects.all()
    return render(request, "mechanic/view_access_mech.html", {"data": data, "cat": categories})


def view_accessories_service(request):
    category_id = request.POST.get('category')

    if category_id:
        data = Products.objects.filter(Category=category_id)
    else:
        data = Products.objects.all()

    categories = Category.objects.all()
    return render(request, "service_center/view_access_service.html", {"data": data, "cat": categories})


def search_products(request):
    # prolist = []
    # data = Products.objects.all()
    # for i in data:
    #     prolist.append(i.Productname.lower())
    #     prolist.append(i.Productname.upper())
    #     prolist.append(i.Productname.title())
    # print(prolist)
    #
    # query = request.GET.get('product')
    # if query in prolist:
    #     products = Products.objects.filter(Productname=query)
    # # if query:
    # #     products = Products.objects.filter(Productname__icontains=query)
    # else:
    #     products = Products.objects.all()

    category_id = request.POST.get('category')

    if category_id:
        products = Products.objects.filter(Category=category_id)
    else:
        products = Products.objects.all()

    query = Category.objects.all()
    return render(request, 'User_Pages/search_products.html', {'products': products, 'query': query})


def search_products_mech(request):
    prolist = []
    data = Products.objects.all()
    for i in data:
        prolist.append(i.Productname.lower())
        prolist.append(i.Productname.upper())
        prolist.append(i.Productname.title())
    print(prolist)

    query = request.GET.get('product')
    if query in prolist:
        products = Products.objects.filter(Productname=query)
    # if query:
    #     products = Products.objects.filter(Productname__icontains=query)
    else:
        products = Products.objects.all()
    return render(request, 'mechanic/search_products_mech.html', {'products': products, 'query': query})


def search_products_service(request):
    prolist = []
    data = Products.objects.all()
    for i in data:
        prolist.append(i.Productname.lower())
        prolist.append(i.Productname.upper())
        prolist.append(i.Productname.title())
    print(prolist)

    query = request.GET.get('product')
    if query in prolist:
        products = Products.objects.filter(Productname=query)
    # if query:
    #     products = Products.objects.filter(Productname__icontains=query)
    else:
        products = Products.objects.all()
    return render(request, 'service_center/search_pro_service.html', {'products': products, 'query': query})


def single_product(request, pid):
    data = Products.objects.get(id=pid)
    return render(request, "User_Pages/single_product.html", {"data": data})


def single_product_mech(request, pid):
    data = Products.objects.get(id=pid)
    return render(request, "mechanic/single_product_mech.html", {"data": data})


def single_product_service(request, pid):
    data = Products.objects.get(id=pid)
    return render(request, "service_center/single_product_service.html", {"data": data})


def addcart(request):
    if request.method == "POST":
        un = request.POST.get("uname")
        pn = request.POST.get("pname")
        q = request.POST.get("qty")
        t = request.POST.get("totalprice")
        if un:
            Cart(username=un, Productname=pn, Quantity=q, Totalprice=t).save()
            messages.success(request, "Added to cart")
            return redirect(indexpage)
        else:
            messages.warning(request, "Register/Login")
            return redirect(indexpage)


def addcart_mech(request):
    if request.method == "POST":
        un = request.POST.get("uname")
        pn = request.POST.get("pname")
        q = request.POST.get("qty")
        t = request.POST.get("totalprice")
        if un:
            Cart(username=un, Productname=pn, Quantity=q, Totalprice=t).save()
            messages.success(request, "Added to cart")
            return redirect(mech_home)
        else:
            messages.warning(request, "Register/Login")
            return redirect(mech_home)


def addcart_service(request):
    if request.method == "POST":
        un = request.POST.get("uname")
        pn = request.POST.get("pname")
        q = request.POST.get("qty")
        t = request.POST.get("totalprice")
        if un:
            Cart(username=un, Productname=pn, Quantity=q, Totalprice=t).save()
            messages.success(request, "Added to cart")
            return redirect(service_home)
        else:
            messages.warning(request, "Register/Login")
            return redirect(service_home)


def cartpage(request):
    # if request.session['Username'] is None:
    #     return redirect(userlogin)
    # else:
    n = request.session.get('Username')
    print(n)

    if n is None:
        messages.warning(request, "Login to go to Cart page")
        return redirect(cartpage)
    else:
        data = Cart.objects.filter(username=n)
        print(data)
        total = 0
        sc = 0
        total1 = 0
        if not data:  # Check if data queryset is empty
            messages.error(request, "Nothing in cart")
        else:
            for item in data:
                if item.Totalprice is not None:  # Ensure Totalprice is not None
                    total += item.Totalprice
                    if total > 500:
                        sc = 50
                    else:
                        sc = 100
                    total1 = total + sc
                    print(total1)
        return render(request, "User_Pages/cart.html", {"data": data, 'total': total, 'sc': sc, 'total1': total1})


def mechcartpage(request):
    data = Cart.objects.filter(username=request.session['Mechname'])
    total = 0
    sc = 0
    total1 = 0
    if not data:  # Check if data queryset is empty
        messages.error(request, "Nothing in cart")
    else:
        for item in data:
            if item.Totalprice is not None:  # Ensure Totalprice is not None
                total += item.Totalprice
                if total > 500:
                    sc = 50
                else:
                    sc = 100
                total1 = total + sc
                print(total1)

    return render(request, "mechanic/mechcart.html", {"data": data, 'total': total, 'sc': sc, 'total1': total1})


def servicecartpage(request):
    data = Cart.objects.filter(username=request.session['Servicename'])
    total = 0
    sc = 0
    total1 = 0
    if not data:  # Check if data queryset is empty
        messages.error(request, "Nothing in cart")
    else:
        for item in data:
            if item.Totalprice is not None:  # Ensure Totalprice is not None
                total += item.Totalprice
                if total > 500:
                    sc = 50
                else:
                    sc = 100
                total1 = total + sc
                print(total1)
    return render(request, "service_center/servicecart.html",
                  {"data": data, 'total': total, 'sc': sc, 'total1': total1})


# def deleteitem(requset,cid):
#     Cart.objects.filter(id=cid).delete()
#     return redirect(cartpage)

def checkoutpage(request):
    data = Cart.objects.filter(username=request.session['Username'])
    print(data)
    total = 0
    sc = 0
    total1 = 0

    if not data:  # Check if data queryset is empty
        messages.error(request, "Nothing in cart")
    else:
        for item in data:
            if item.Totalprice is not None:  # Ensure Totalprice is not None
                total += item.Totalprice
                if total > 500:
                    sc = 50
                else:
                    sc = 100
                total1 = total + sc
                print(total1)

    return render(request, "User_Pages/checkout.html", {"data": data, 'total': total, 'sc': sc, 'total1': total1})


def mechcheckoutpage(request):
    data = Cart.objects.filter(username=request.session['Mechname'])
    print(data)
    total = 0
    sc = 0
    total1 = 0

    if not data:  # Check if data queryset is empty
        messages.error(request, "Nothing in cart")
    else:
        for item in data:
            if item.Totalprice is not None:  # Ensure Totalprice is not None
                total += item.Totalprice
                if total > 500:
                    sc = 50
                else:
                    sc = 100
                total1 = total + sc
                print(total1)

    return render(request, "mechanic/mechcheckout.html", {"data": data, 'total': total, 'sc': sc, 'total1': total1})


def servicecheckoutpage(request):
    data = Cart.objects.filter(username=request.session['Servicename'])
    print(data)
    total = 0
    sc = 0
    total1 = 0

    if not data:  # Check if data queryset is empty
        messages.error(request, "Nothing in cart")
    else:
        for item in data:
            if item.Totalprice is not None:  # Ensure Totalprice is not None
                total += item.Totalprice
                if total > 500:
                    sc = 50
                else:
                    sc = 100
                total1 = total + sc
                print(total1)

    return render(request, "service_center/servicecheckout.html",
                  {"data": data, 'total': total, 'sc': sc, 'total1': total1})


def payment(request):

    if request.method == "POST":
        un = request.POST.get("un")
        email = request.POST.get("email")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        msg = request.POST.get("bill")
        total = request.POST.get("total")
        # cart=Cart.objects.get(username=un)

        Order(uname=un, Email=email, Phone=phone, Address=address, Message=msg, Totalprice=total).save()
        return redirect(payment_page)


def payment_page(req):
    data = Order.objects.order_by('-id').first()
    pay = data.Totalprice
    amount = int(pay * 100)
    pay_str = str(amount)

    for i in pay_str:
        print(i)
    if req.method == "POST":
        order_currency = "INR"
        client = razorpay.Client(auth=('rzp_test_CagytDuj1DwsMy', 'jMzxj0rpJ7T0ldH7zQi904Zb'))
        payment = client.order.create({'amount': amount, 'currency': order_currency, 'payment_capture': '1'})
    return render(req, "User_Pages/payment.html", {'customer': data, 'pay_str': pay_str})


from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def send_notification(request, mechanic_id):
    user_request = {
        'message': 'User request for breakdown assistance'
    }

    # mechanic_id = request.POST.get('mechanic_id')  # Example: Get mechanic ID from request

    # Send notification to specific  mechanic via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'mechanic_{mechanic_id}',
        {
            'type': 'send_notification',
            'message': 'User request for breakdown assistance'
        }
    )
    print("hi")
    return redirect(search_nearest_locations)


def home(request):
    return render(request, 'home.html')




def chat_room(request, user_id, mechanic_id):
    user = get_object_or_404(userdatas, Userid=user_id)
    mechanic = get_object_or_404(Mechanics, Mechid=mechanic_id)
    room_name = f'user_{user_id}_mechanic_{mechanic_id}'
    print(room_name)
    messages = chatmessage.objects.filter(room_name=room_name).order_by('timestamp')

    return render(request, 'User_Pages/chat.html', {
        'room_name': room_name,
        'messages': messages,
        'user': user,
        'mechanic': mechanic,
    })





import logging

logger = logging.getLogger(__name__)


def convert_to_timezone(utc_datetime_str, timezone_str):
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
    utc_datetime = pytz.utc.localize(utc_datetime)  # Localize as UTC
    local_timezone = pytz.timezone(timezone_str)  # Create timezone object
    local_datetime = utc_datetime.astimezone(local_timezone)  # Convert to local timezone
    return local_datetime


def mechanic_chat(request, user_id):
    if not request.session.get('Mechid'):
        return redirect(mechlogin)
    # request.session['Userid'] = user_id  # Ensure session data is set

    try:
        mechanic = Mechanics.objects.get(pk=request.session.get('Mechid'))
        user = userdatas.objects.get(pk=user_id)
    except (Mechanics.DoesNotExist, userdatas.DoesNotExist):
        logger.error(f"Mechanic or user not found. Mechanic ID: {request.session.get('Mechid')}, User ID: {user_id}")
        return redirect('error_page')
    token = generate_token(request.session.get('Mechid'), 'mechanic')

    room_name = f"user_{user_id}_mechanic_{mechanic.Mechid}"
    messages = chatmessage.objects.filter(room_name=room_name).order_by('timestamp')
    # Count unread messages
    # unread_message_count = chatmessage.objects.filter(
    #     room_name=room_name,
    #     receiver_id=mechanic.Mechid,
    #     read_by__isnull=True
    # ).count()
    return render(request, 'mechanic/chat.html', {
        'user': user,
        'mechanic': mechanic,
        'room_name': room_name,
        'messages': messages,
        'token': token,
        'currentUserType': 'mechanic',
        'currentUserId': mechanic.Mechid,
        # 'userid':user_id,
        # 'mechid':mechanic.Mechid
    })


def user_chat(request, mechanic_id):
    if not request.session.get('Userid'):
        return redirect(loginuser)

    try:
        user = userdatas.objects.get(pk=request.session.get('Userid'))
        mechanic = Mechanics.objects.get(pk=mechanic_id)

    except (userdatas.DoesNotExist, Mechanics.DoesNotExist):
        return redirect('error_page')  # Handle the case where the user or mechanic does not exist

    room_name = f"user_{user.Userid}_mechanic_{mechanic.Mechid}"
    messages = chatmessage.objects.filter(room_name=room_name).order_by('timestamp')
    token = generate_token(request.session.get('Userid'), 'user')

    # local_datetime = convert_to_timezone(utc_datetime_str, timezone_str)
    return render(request, 'User_Pages/chat.html', {
        'user': user,
        'mechanic': mechanic,
        'room_name': room_name,
        'messages': messages,
        'token': token,
        'currentUserType': 'user',
        'currentUserId': user.Userid,
        # 'local_timestamp': messages.timestamp.astimezone(local_timezone)

    })



def delete_cart(req, cid):
    Cart.objects.filter(id=cid).delete()
    return redirect(cartpage)


def delete_cart_mech(req, cid):
    Cart.objects.filter(id=cid).delete()
    return redirect(mechcartpage)


def delete_cart_service(req, cid):
    Cart.objects.filter(id=cid).delete()
    return redirect(servicecartpage)






