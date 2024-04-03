import re
import json
import random
import datetime
# django
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.utils.html import strip_tags
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,Group
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate,login,logout
from request_and_bookings.forms import FlightReturnForm
#local
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view,renderer_classes, permission_classes

from . forms import *
from reviews.models import Reviews
from main.models import Country, Status
from employee.models import EmployeeService
from request_and_bookings.models import Request
from web.functions import generate_member_form_errors
from deals.models import Deals, DealsReview, InterestedDeals
from main.decorators import member_login_required, role_required
from members.models import FamilyMember, Member, MemberDocuments, MemberSettings
from main.functions import decrypt_message, encrypt_message, get_auto_id, send_email
from web.forms import MemberForgotPasswordForm, MemberPasswordGenerationForm,MemberLoginForm
from web.serializers import DealReviewSerializers, DealsSerializers, MemberSettingsSerializers, PhoneCodeSerializers

# Create your views here.
@member_login_required
@role_required(['member'])
def profile_protected(request):
    if MemberSettings.objects.filter(member__user=request.user).exists() :
        
        protection = MemberSettings.objects.get(member__user=request.user).password_protection
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": "true",
            "protection_status": protection,
        }
    else:
        
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": "false",
            "message": "user not found",
        }
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
    

def deals_by_type(request):
    deal_type = request.GET.get('deal_type')
    # print(deal_type)
    
    if deal_type:
        deals = Deals.objects.filter(is_deleted=False)
        if deal_type!="hotdeal":
            deals = deals.filter(service__name=deal_type)
        else:
            deals = deals.filter(is_hot_deal=True)
            
        deals = deals.order_by("-date_added")[:3]
            
        serialized = DealsSerializers(deals, many=True, context={"request":request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status" : "true",
            "data" : serialized.data,
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        response_data = {
            "status" : "false",
            "title" : "Not Found",
            "message" : "deals not found",
        }
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")

def phone_code(request):
    phone_code = request.GET.get('phone_code')
    
    if (instances:=Country.objects.all()).exists():
        if phone_code:
            filter_data = {}
            
            instances = instances.filter(
                Q(phone_code__icontains=phone_code)
            )
            title = "Phonecode - %s" % phone_code
            filter_data['q'] = phone_code
                    
        serialized = PhoneCodeSerializers(instances, many=True, context={"request":request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status" : "true",
            "data" : serialized.data,
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        response_data = {
            "status" : "false",
            "title" : "Not Found",
            "message" : "deals not found",
        }
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")

def member_index(request):
    deals = Deals.objects.filter(is_active=True).order_by("-id")
    join_form = MemberJoinUsForm()
    reviews = Reviews.objects.filter(is_deleted=False)
    
    phone_country = Country.objects.all()
    
    deal_count = deals.count()
    reviews_count = reviews.count()
    
    context = {
        'deals': deals,
        'form': join_form,
        'reviews': reviews,
        'deal_count': deal_count,
        'reviews_count': reviews_count,
        'phone_country': phone_country,
    }
    return render(request,'member_panel/pages/landing_page.html',context)

def privacy_policy(request):
    return render(request, 'member_panel/pages/privacy.html')

def terms_and_conditions(request):
    return render(request, 'member_panel/pages/terms_and_conditions.html')

@member_login_required
@role_required(['member'])
def member_home(request):
    service_name = request.GET.get("service")
    current_date = datetime.date.today()
    
    deals = Deals.objects.filter(is_active=True).order_by("-date_added")
    hot_deals = Deals.objects.filter(is_active=True,is_hot_deal=True).order_by("-date_added")
    ucoming_bookings = Request.objects.filter(member_id__user=request.user,service_date__gte=current_date,status__title="Booking Completed").order_by("-date_added")
    my_requests = Request.objects.filter(member_id__user=request.user).exclude(status__title="Booking Completed").order_by("-date_added")
    
    # request forms
    flight_form = FlightRequestForm()
    flight_return_form = FlightReturnForm()
    
    taxi_form = TaxiRequestForm()
    tempo_form = TempoRequestForm()
    bus_form = BusRequestForm()
    train_form = TrainRequestForm()
    
    hotel_form = HotelRequestForm()
    hotel_age_below_form = HotelChildAgeBelowThreeForm()
    hotel_age_abouve_form = HotelChildAgeAboveThreeForm()
    
    holiday_form = HolidaysRequestForm()
    passport_form = PassportRequestForm()
    visa_form = VisaRequestForm()
    aboad_from = StudyAbroudRequestForm()
    enquiry_form = OtherRequestForm()
    
    if service_name:
        if service_name!="hotdeal":
            deals = deals.filter(service__name=service_name)
        else:
            deals = deals.filter(is_hot_deal=True)
    
    context = {
        'deals': deals[:3],
        'hot_deals': hot_deals,
        'ucoming_bookings': ucoming_bookings,
        'my_requests': my_requests,
        
        'flight_form': flight_form,
        'flight_return_form': flight_return_form,
        'taxi_form': taxi_form,
        'tempo_form': tempo_form,
        'bus_form': bus_form,
        'train_form': train_form,
        
        'hotel_form': hotel_form,
        'hotel_age_below_form': hotel_age_below_form,
        'hotel_age_abouve_form': hotel_age_abouve_form,
        
        'holiday_form': holiday_form,
        'passport_form': passport_form,
        'visa_form': visa_form,
        'aboad_from': aboad_from,
        'enquiry_form': enquiry_form,
        
        'current_date' : current_date,
        'home_page': True,
        'service_name': service_name,
        
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request,'member_panel/pages/home.html',context)

@member_login_required
@role_required(['member'])
def create_flight_request(request):
    response_data = {}

    flight_request_form = FlightRequestForm(request.POST,files=request.FILES)

    if flight_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Flight")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = flight_request_form.cleaned_data["preferred_departure_date"],
        )
        
        #create flight request
        service_data = flight_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(FlightBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        
        if request.POST.get('trip_type') == "Round Trip" :
            FlightReturn.objects.create(
                flight_booking_id = service_data,
                departure_date = flight_request_form.cleaned_data['return_date'],
            )
        
        # create comment
        if request.POST.get("flight_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("flight_comment"),
            )
        
        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Flight Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(flight_request_form, formset=False)
        print(message)
        
        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_taxi_request(request):
    response_data = {}

    taxi_request_form = TaxiRequestForm(request.POST,files=request.FILES)

    if taxi_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Taxi")
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = taxi_request_form.cleaned_data["taxi_pickup_date"],
        )
        
        #create taxi request
        service_data = taxi_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(TaxiBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
            
        service_data.save()
        # create comment
        if request.POST.get("taxi_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("taxi_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Taxi Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(taxi_request_form, formset=False)
        print(message)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_tempo_request(request):
    response_data = {}

    tempo_request_form = TempoRequestForm(request.POST,files=request.FILES)

    if tempo_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Tempo")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = tempo_request_form.cleaned_data["tempo_pickup_date"],
        )
        
        #create tempo request
        service_data = tempo_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(TempoBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("tempo_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("tempo_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Tempo Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(tempo_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_bus_request(request):
    response_data = {}

    bus_request_form = BusRequestForm(request.POST,files=request.FILES)

    if bus_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Bus")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = bus_request_form.cleaned_data["bus_pickup_date"],
        )
        
        #create bus request
        service_data = bus_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(BusBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("bus_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("bus_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Bus Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(bus_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_train_request(request):
    response_data = {}

    train_request_form = TrainRequestForm(request.POST,files=request.FILES)

    if train_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Train")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = train_request_form.cleaned_data["train_prefered_travel_date"],
        )
        
        #create train request
        service_data = train_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(TrainBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("train_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("train_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Train Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(train_request_form, formset=False)
        # print(message)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_hotel_request(request):
    response_data = {}

    hotel_request_form = HotelRequestForm(request.POST,files=request.FILES)

    if hotel_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Hotels")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = hotel_request_form.cleaned_data["hotel_check_in_date"],
        )
        
        #create hotel request
        service_data = hotel_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(HotelBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        
        if hotel_request_form.cleaned_data["hotel_number_of_children"] == 1 or hotel_request_form.cleaned_data["hotel_number_of_children"] == 2:
            if hotel_request_form.cleaned_data["hotel_number_of_children"] == 1 :
                HotelChildAgeBelowThree.objects.create(
                    hotel_child_age_one = request.POST.get("hotel_child_age_one"),
                    hotel_request_id = service_data,
                )
                HotelChildAge.objects.create(
                    child_ages=[int(request.POST.get("hotel_child_age_one"))],
                    hotel_request_id = service_data,
                )
            elif hotel_request_form.cleaned_data["hotel_number_of_children"] == 2 :
                HotelChildAgeBelowThree.objects.create(
                    hotel_child_age_one = request.POST.get("hotel_child_age_one"),
                    hotel_child_age_two = request.POST.get("hotel_child_age_two"),
                    hotel_request_id = service_data,
                )
                HotelChildAge.objects.create(
                    child_ages=[int(request.POST.get("hotel_child_age_one")),int(request.POST.get("hotel_child_age_two"))],
                    hotel_request_id = service_data,
                )
        elif hotel_request_form.cleaned_data["hotel_number_of_children"] >= 3 :
            HotelChildAgeAboveThree.objects.create(
                hotel_younger_child_age = request.POST.get("hotel_younger_child_age"),
                hotel_elder_child_age = request.POST.get("hotel_elder_child_age"),
                hotel_request_id = service_data,
            )
            
            age=[]
            younger_age=int(request.POST.get("hotel_younger_child_age"))
            elder_age=int(request.POST.get("hotel_elder_child_age"))
            if younger_age:
                for i in range(1,younger_age):
                    age.append(5)
            if elder_age:
                for i in range(1,elder_age):
                    age.append(5)
            HotelChildAge.objects.create(
                child_ages=age,
                hotel_request_id = service_data,
            )
                    
            
        
        # create comment
        if request.POST.get("hotel_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("hotel_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Hotel Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(hotel_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_holiday_request(request):
    response_data = {}

    holiday_request_form = HolidaysRequestForm(request.POST,files=request.FILES)

    if holiday_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Holiday")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = holiday_request_form.cleaned_data["holidays_travel_date"],
        )
        
        #create holiday request
        service_data = holiday_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(HolidaysBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("holiday_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("holiday_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Holiday Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(holiday_request_form, formset=False)
        print(message)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_visa_request(request):
    response_data = {}

    visa_request_form = VisaRequestForm(request.POST,files=request.FILES)

    if visa_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Visa")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = datetime.datetime.today(),
        )
        
        #create visa request
        service_data = visa_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(VisaBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("visa_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("visa_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Visa Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(visa_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_passport_request(request):
    response_data = {}

    passport_request_form = PassportRequestForm(request.POST,files=request.FILES)

    if passport_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Passport")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
            service_date = datetime.datetime.today(),
        )
        
        #create passport request
        service_data = passport_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(PassportBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("passport_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("passport_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Passport Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(passport_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_aboad_request(request):
    response_data = {}

    abroad_request_form = StudyAbroudRequestForm(request.POST,files=request.FILES)

    if abroad_request_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Study Abroad")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
        )
        
        #create abroad request
        service_data = abroad_request_form.save(commit=False)
        service_data.auto_id = get_auto_id(AbroudBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("abroad_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("abroad_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Study Abroad Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(abroad_request_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_insurance_request(request):
    response_data = {}
    
    checked_insurences = False
    insurance_type = request.POST.getlist('insurances[]')
    if insurance_type :
        checked_insurences = True

    if checked_insurences:
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Insurance")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
        )
        
        #create Insurance request
        for types in insurance_type:
            type_instance = InsuranceType.objects.get(id=types)
            InsuranceBookingRequest.objects.create(
                auto_id = get_auto_id(InsuranceBookingRequest),
                creator = request.user,
                date_updated = datetime.datetime.today(),
                updater = request.user,
                insurance_type = type_instance,
                request_id = request_data,
            )
            
        # create comment
        if request.POST.get("insurance_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("insurance_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Insurance Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = "insurance : check any insurance type"

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


@member_login_required
@role_required(['member'])
def create_enquiry(request):
    response_data = {}

    enquiry_form = OtherRequestForm(request.POST)

    if enquiry_form.is_valid():
        # print("valid")
        request_auto_id = get_auto_id(Request)
        regid = "RQ" + str(request_auto_id).zfill(4)
        request_status = Status.objects.get(title="Request Pending")
        service_category = Services.objects.get(name="Other")
        
        import random
        
        service_employees = EmployeeService.objects.filter(service=service_category)
        service_employees = service_employees.values_list('emp_id', flat=True)

        if service_employees:
            items = list(Employee.objects.filter(pk__in=service_employees))
        else:
            items = list(Employee.objects.all())

        number_of_random_items = 1
        employee_items = random.sample(items, number_of_random_items)
        selected_employee = employee_items[0]
        employee_instance = Employee.objects.get(pk=uuid.UUID(str(selected_employee.pk)))
        
        request_data = Request.objects.create(
            auto_id = request_auto_id,
            request_id = regid,
            creator = request.user,
            date_updated = datetime.datetime.today(),
            updater = request.user,
            status = request_status,
            service_category = service_category,
            assigned_to = employee_instance,
            member_id = Member.objects.get(user=request.user),
        )
        
        #create abroad request
        service_data = enquiry_form.save(commit=False)
        service_data.auto_id = get_auto_id(OtherBookingRequest)
        service_data.creator = request.user
        service_data.date_updated = datetime.datetime.today()
        service_data.updater = request.user
        service_data.user = request.user
        service_data.request_id = request_data
        service_data.save()
        # create comment
        if request.POST.get("en_service_comment"):
            RequestComment.objects.create(
                request_id = request_data,
                author_id = request.user,
                comment = request.POST.get("en_service_comment"),
            )

        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Enquiry Request sent successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:member_home')
        }

    else:
        message = generate_member_form_errors(enquiry_form, formset=False)

        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript',status=status_code)


# @member_login_required
# @role_required(['member'])
def deal_details(request,pk):
    
    instance = Deals.objects.get(pk=pk)
    deal_reviews = DealsReview.objects.filter(deal=instance).exclude(Q(status='30') | Q(status='Reject'))
    interested_memebers = InterestedDeals.objects.filter(deal=instance)
    
    is_interested = False
    if request.user.is_authenticated and interested_memebers.filter(member__user=request.user).exists():
        is_interested = True
        
    context = {
        'instance': instance,
        'deal_reviews': deal_reviews,
        'interested_memebers': interested_memebers,
        'is_interested': is_interested,
        
        'deals_page': True,
    }
  
    return render(request,'member_panel/pages/deals-details.html',context)


def interested_deal_members(request):
    response_data = {}
    deal_id = request.GET.get("deal_id")
    
    interested_members = InterestedDeals.objects.filter(deal__pk=deal_id)
    member_pks = interested_members.values_list('member__pk', flat=True)
    members = Member.objects.filter(pk__in=member_pks)
    
    member_details = [] 
    
    for member in members:
        member_data = {
            "name": member.fullname(),  
            "designation": member.profession.name,
            "initial": member.get_initial(),
            # "image": member.image.url if member.image else None
        }
        member_details.append(member_data)
    
    response_data = {
        "status": "true",
        "title": "Successfully",
        "message": "",
        "members": member_details
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


    
@member_login_required
@role_required(['member'])
def add_review(request):
    response_data = {}
    
    deal_id = request.GET.get("deal_id")
    
    deal = Deals.objects.get(pk=deal_id)
    member = Member.objects.get(user=request.user, is_deleted=False)
    review = request.GET.get("review_text")
    
    if deal and review:
        deal_review = DealsReview.objects.create(
            deal=deal,
            member=member,
            review=review,
            status="10",
            date_time=datetime.datetime.today(),
        )
        
        status_code = status.HTTP_200_OK           
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "created successfully.",
            'redirect': 'true',
            "redirect_url": reverse('web:deal_details', kwargs={'pk': deal_id})
        }
        
    else:
        message = "add review"

        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": message,
        }

    return HttpResponse(json.dumps(response_data), content_type='application/json', status=status_code)


@member_login_required
@role_required(['member'])
def profile(request):
    instance = Member.objects.get(user=request.user,is_deleted=False)
    family_instances = FamilyMember.objects.filter(member_id=instance)
    member_documents = MemberDocuments.objects.filter(member_id=instance)
    
    settings_instance = ""
    if MemberSettings.objects.filter(member=instance).exists():
        settings_instance = MemberSettings.objects.get(member=instance)
        
    password_form = UserPasswordChangeForm(request.user)
    
    context = {
        'instance': instance,
        'family_instances': family_instances,
        'member_documents': member_documents,
        'settings_instance': settings_instance,
        'password_form': password_form,
        'profile_page': True,
    }
  
    return render(request,'member_panel/pages/profile.html',context)


@member_login_required
@role_required(['member'])
def profile_settings_update(request):
    member = Member.objects.get(user=request.user,is_deleted=False)
    
    email_notification = request.GET.get("email_notification")
    whatsapp_notification = request.GET.get("whatsapp_notification")
    password_protection = request.GET.get("password_protection")
    
    if MemberSettings.objects.filter(member=member).exists():
        MemberSettings.objects.filter(member=member).update(
            email_notification = email_notification,
            whatsapp_notification = whatsapp_notification,
            password_protection = password_protection,
        )
        
    else:
        MemberSettings.objects.create(
            member = member,
            email_notification = email_notification,
            whatsapp_notification = whatsapp_notification,
            password_protection = password_protection,
        )
        
    member_setings = MemberSettings.objects.get(member=member)
    serialized = MemberSettingsSerializers(member_setings, many=False, context={"request":request})
    
    response_data = {
        "StatusCode": 200,
        "data": serialized.data,
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/json', status=status.HTTP_200_OK)


@member_login_required
@role_required(['member'])
def change_user_password(request):

    """
    change user password for current user
    :param request:
    :param pk:
    :return:
    """

    response_data = {}
    message = ''
    
    form = UserPasswordChangeForm(request.user,request.POST)

    if form.is_valid():
        form.save()
        
        status_code=status.HTTP_200_OK
        response_data = {
            "status": "true",
            "title": "Successfull",
            "message": "Password changed",
            "redirect": 'true',
            "redirect_url": reverse('web:member_logout')
        }
    else:
        
        status_code=status.HTTP_400_BAD_REQUEST
        message = generate_member_form_errors(form, formset=False)
        
        response_data = {
            "status": "false",
            "message": message,
        }
        
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
    

@member_login_required
@role_required(['member'])
def deal_interest(request,pk):
    
    instance = Deals.objects.get(pk=pk)
    member = Member.objects.get(user=request.user)
    
    if InterestedDeals.objects.filter(deal=instance,member=member).exists():
        InterestedDeals.objects.filter(deal=instance,member=member).delete()
        
        status_code = status.HTTP_200_OK
        interested_count = InterestedDeals.objects.filter(deal=instance).count()
        response_data = {
            "status": "true",
            "interested_status": "false",
            "message": "not interest",
            "interested_count": interested_count,
        }
        
    else:
        InterestedDeals.objects.create(
            deal = instance,
            member = member,
        )
        status_code = status.HTTP_200_OK
        interested_count = InterestedDeals.objects.filter(deal=instance).count()
        response_data = {
            "status": "true",
            "interested_status": "true",
            "message": "interested",
            "interested_count": interested_count,
        }
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")


@member_login_required
@role_required(['member'])
def deal_list(request):
    
    service_name = request.GET.get("service")
    current_date = timezone.now().date()
    instances = Deals.objects.filter(is_deleted=False, is_active=True).order_by("-date_added")
    instances = instances.filter(end_date__isnull=True) | instances.filter(end_date__gte=current_date)
    print(service_name)
    if service_name:
        if service_name!="hotdeal":
            instances = instances.filter(service__name=service_name)
            
        else:
            instances = instances.filter(is_hot_deal=True)
        
    context = {
        'instances': instances,
        'deals_page': True,
        'service_name': service_name,
    }
  
    return render(request,'member_panel/pages/deals_list.html',context)


@member_login_required
@role_required(['member'])
def my_bookings(request):
    import datetime
    service = request.GET.get("service")
    current_date = datetime.date.today()
    
    request_instances = Request.objects.filter(member_id__user=request.user,is_deleted=False).order_by('-date_added')
    
    if service:
        request_instances = request_instances.filter(service_category__section_name=service)
    
    upcoming_instances = request_instances.filter(member_id__user=request.user,service_date__gte=current_date,status__title="Booking Completed")
    completed_instances = request_instances.filter(member_id__user=request.user,service_date__lt=current_date,status__title="Booking Completed")
    
    # request forms
    flight_form = FlightRequestForm()
    taxi_form = TaxiRequestForm()
    tempo_form = TempoRequestForm()
    bus_form = BusRequestForm()
    train_form = TrainRequestForm()
    hotel_form = HotelRequestForm()
    holiday_form = HolidaysRequestForm()
    passport_form = PassportRequestForm()
    visa_form = VisaRequestForm()
    aboad_from = StudyAbroudRequestForm()
    enquiry_form = OtherRequestForm()
        
    context = {
        'upcoming_instances': upcoming_instances,
        'completed_instances': completed_instances,
        'current_date' : current_date,
        
        'flight_form': flight_form,
        'taxi_form': taxi_form,
        'tempo_form': tempo_form,
        'bus_form': bus_form,
        'train_form': train_form,
        'hotel_form': hotel_form,
        'holiday_form': holiday_form,
        'passport_form': passport_form,
        'visa_form': visa_form,
        'aboad_from': aboad_from,
        'enquiry_form': enquiry_form,
        
        'service': service,
        'my_booking_page': True,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
  
    return render(request,'member_panel/pages/my_booking.html',context)


def member_login(request):
    
    if request.method == 'POST':
        form = MemberLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            
            if not '@' in username:
                username = username.upper()
                
                if Member.objects.filter(member_id=username).exists():
                    if Member.objects.filter(member_id=username,is_active=True).exists():
                        username = Member.objects.get(member_id=username).email
                        if User.objects.filter(username=username).exists():
                            user = authenticate(username=username, password=password)
                            if user is not None:
                                login(request, user)
                                response_data = {
                                    "status": "true",
                                    "title": "Successful",
                                    "message": "Login success",
                                }
                                status_code = status.HTTP_200_OK
                            else:
                                status_code = status.HTTP_400_BAD_REQUEST
                                response_data = {
                                    "status": "false",
                                    "message": "username and password do not match",
                                }
                            return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                            # return JsonResponse(response_data, status=status_code)
                        else:
                            status_code = status.HTTP_400_BAD_REQUEST
                            response_data = {
                                "status": "false",
                                "message": "Incorrect username or password",
                            }
                            return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                            # return JsonResponse(response_data, status=status_code)
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response_data = {
                            "status": "false",
                            "message": "Your Account is blocked. Please contact TTCLUB Admin",
                        }
                        return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "status": "false",
                        "message": "Incorrect username or password",
                    }
                    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                    # return JsonResponse(response_data, status=status_code)
            else:
                if Member.objects.filter(email=username).exists():
                    if Member.objects.filter(email=username,is_active=True).exists():
                        if User.objects.filter(username=username).exists():
                            user = authenticate(username=username, password=password)
                            if user is not None:
                                login(request, user)
                            
                                response_data = {
                                    "status": "true",
                                    "title": "Successful",
                                    "message": "Login success",
                                }
                                status_code = status.HTTP_200_OK
                            else:
                                status_code = status.HTTP_400_BAD_REQUEST
                                response_data = {
                                    "status": "false",
                                    "message": "username and password do not match",
                                }
                            return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                        else:
                            status_code = status.HTTP_400_BAD_REQUEST
                            response_data = {
                                "status": "false",
                                "message": "Incorrect username or password",
                            }
                            return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response_data = {
                            "status": "false",
                            "message": "Your Account is blocked. Please contact TTCLUB Admin",
                        }
                        return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "status": "false",
                        "message": "Incorrect username or password",
                    }
                    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
        else:
            message = generate_member_form_errors(form, formset=False)
            response_data = {
                "status": "false",
                "message": message,
            }
            return HttpResponse(json.dumps(response_data),status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
            # return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
    else :
        form = MemberLoginForm()
        
        context = {
            'form': form,
            'url': reverse('web:member_login')
        }
    
        return render(request,'member_panel/registration/login.html',context)


# def member_forgot_password(request):
    
#     if request.method == 'POST':
#         form = MemberForgotPasswordForm(request.POST)
        
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             member_data = Member.objects.get(email=email)
            
#             encrypt_id = encrypt_message(member_data.member_id)
#             base_url = request.scheme + "://" + request.get_host()
#             print(base_url)
#             mail_html = render_to_string('member_panel/registration/change_password_mail_content.html', {'member_data': member_data, 'logo_url': 'https://qiprojects.in/static/admin_panel/assetss/images/icons/logo/ttclubmaillogo.png', 'encrypt_id':encrypt_id,'base_url':base_url})
#             # print(mail_html)
#             mail_message = strip_tags(mail_html)
#             send_email("TTCLUB Member Password Change",form.cleaned_data['email'],mail_message,mail_html)
            
#             response_data = {
#                 "status": "true",
#                 "title": "Successfull",
#                 "message": "login success",
#                 "redirect_url": reverse('web:member_forgot_password_success', kwargs={'member_id': encrypt_id}),
#                 }
            
#             return HttpResponse(json.dumps(response_data),status=status.HTTP_200_OK, content_type="application/json")
            
#         else:
#             message = generate_member_form_errors(form, formset=False)
            
#             response_data = {
#                 "status": "false",
#                 "message": message,
#             }
#             return HttpResponse(json.dumps(response_data),status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
#     else :
#         form = MemberForgotPasswordForm()
        
#         context = {
#             'form': form,
#             'url': reverse('web:member_forgot_password')
#         }
  
#         return render(request,'member_panel/registration/forgot_password.html',context)


def member_forgot_password(request):
    if request.method == 'POST':
        form = MemberForgotPasswordForm(request.POST)

        if form.is_valid():
            email_or_member_id = form.cleaned_data['email_or_member_id']
            member_data = None  # Initialize member_data to None

            if '@' in email_or_member_id:
                # User provided an email
                try:
                    member_data = Member.objects.get(email=email_or_member_id)
                except Member.DoesNotExist:
                    # Handle the case where the email is not found
                    response_data = {
                        "status": "false",
                        "message": "Email not found",
                    }
                    return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type="application/json")
            else:
                # User provided a member ID
                try:
                    member_data = Member.objects.get(member_id=email_or_member_id)
                except Member.DoesNotExist:
                    # Handle the case where the member ID is not found
                    response_data = {
                        "status": "false",
                        "message": "Member ID not found",
                    }
                    return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type="application/json")

            encrypt_id = encrypt_message(member_data.member_id)
            base_url = request.scheme + "://" + request.get_host()
            mail_html = render_to_string('member_panel/registration/change_password_mail_content.html', {'member_data': member_data, 'logo_url': 'https://qiprojects.in/static/admin_panel/assetss/images/icons/logo/ttclubmaillogo.png', 'encrypt_id':encrypt_id,'base_url':base_url})
            mail_message = strip_tags(mail_html)
            send_email("Request To Reset Password", member_data.email, mail_message, mail_html)

            response_data = {
                "status": "true",
                "title": "Successfull",
                "message": "login success",
                "redirect_url": reverse('web:member_forgot_password_success', kwargs={'member_id': encrypt_id}),
            }

            return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK, content_type="application/json")

        else:
            message = generate_member_form_errors(form, formset=False)

            response_data = {
                "status": "false",
                "message": message,
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
    else:
        form = MemberForgotPasswordForm()

        context = {
            'form': form,
            'url': reverse('web:member_forgot_password')
        }

        return render(request, 'member_panel/registration/forgot_password.html', context)
    

def change_password(request,member_id):

    """
    change password for member
    :param request:
    :param pk:
    :return:
    """

    response_data = {}
    decrypt_id = decrypt_message(member_id)
    message = ''
    
    if Member.objects.filter(member_id=decrypt_id).exists():
        instance = Member.objects.get(member_id=decrypt_id)
        
        if request.method == 'POST':
            form = MemberPasswordGenerationForm(request.POST,files=request.FILES,instance=instance)

            if form.is_valid():
                if form.cleaned_data['password']==form.cleaned_data['confirm_password']:
                    usr = User.objects.get(username=instance.email)
                    usr.set_password(form.cleaned_data['password'])
                    usr.save()

                    # Edit member
                    instance.date_updated = datetime.datetime.today()
                    instance.updater = usr
                    instance.is_active = True
                    instance.save()
                    
                    status_code=status.HTTP_200_OK
                    response_data = {
                        "status": "true",
                        "title": "Successfull",
                        "message": "Password changed",
                    }
                else:
                    message = "Passwords do not match"
                    status_code=status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "status": "false",
                        "message": message,
                    }
                    
                return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
            else:
                # print("not valid")
                message = generate_member_form_errors(form, formset=False)
                response_data = {
                    "status": "false",
                    "message": message,
                }
                
            return HttpResponse(json.dumps(response_data),status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
            
        else :
            form = form = MemberPasswordGenerationForm()

            context = {
                'form': form,
                'member_id': member_id,
            }
        
            return render(request,'member_panel/password_change/member_password.html', context)
    else :
        form = MemberForgotPasswordForm()
        
        context = {
            'form': form,
            'error_message': "member not found",
            'url': reverse('web:member_forgot_password')
        }
  
        return render(request,'member_panel/registration/forgot_password.html',context)
    

def member_forgot_password_success(request,member_id):
    
    base_url = request.scheme + "://" + request.get_host()
    
    context = {
        'encrypt_id': member_id,
        'base_url': base_url
    }
  
    return render(request,'member_panel/registration/change_password_mail_success.html',context)


def member_resend_forgot_link(request,member_id):
    
    decrypt_id = decrypt_message(member_id)
    member_data = Member.objects.get(member_id=decrypt_id)
    
    base_url = request.scheme + "://" + request.get_host()
    # print(base_url)
    mail_html = render_to_string('member_panel/registration/change_password_mail_content.html', {'member_data': member_data, 'logo_url': 'https://qiprojects.in/static/admin_panel/assetss/images/icons/logo/ttclubmaillogo.png', 'encrypt_id':member_id,'base_url':base_url})
    # print(mail_html)
    mail_message = strip_tags(mail_html)
    send_email("Request To Reset Password",member_data.email,mail_message,mail_html)
    
    context = {
        'encrypt_id': member_id,
        'base_url': base_url
    }
  
    return render(request,'member_panel/registration/change_password_mail_success.html',context)


def create_password(request,member_id):

    """
    create password for member
    :param request:
    :param pk:
    :return:
    """

    response_data = {}
    decrypt_id = decrypt_message(member_id)
    instance = Member.objects.get(member_id=decrypt_id)
    message = ''
    if not instance.password :
        if request.method == 'POST':
            form = MemberPasswordGenerationForm(request.POST,files=request.FILES,instance=instance)

            if form.is_valid():
                if form.cleaned_data['password']==form.cleaned_data['confirm_password']:
                    # print("is valid")
                    usr = User.objects.get(username=instance.email)
                    usr.set_password(form.cleaned_data['password'])
                    usr.save()

                    # Edit member
                    instance.date_updated = datetime.datetime.today()
                    instance.updater = usr
                    instance.is_active = True
                    instance.password = encrypt_message(form.cleaned_data['password'])
                    instance.save()

                    response_data = {
                        "status": "true",
                        "title": "Successful",
                        "message": "Password generated",
                    }
                    status_code = status.HTTP_200_OK
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "status": "false",
                        "message": "Passwords do not match",
                    }
                return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")
            else:
                # print("not valid")
                message = generate_member_form_errors(form, formset=False)
                # print(message)
                response_data = {
                    "status": "false",
                    "message": message,
                }
                
                return HttpResponse(json.dumps(response_data),status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
            
        else :
            form = form = MemberPasswordGenerationForm(instance=instance)

            context = {
                'form': form,
                'member_id': member_id,
            }
        
            return render(request,'member_panel/password_change/member_password.html', context)
    else:
        
        return redirect(reverse('web:member_password_successfull'))
        
        
def member_password_successfull(request):
  
    return render(request,'member_panel/password_change/password-success.html')


def joinus(request):

    """
    send mail for joinus details
    :param request:
    :param pk:
    :return:
    """

    response_data = {}
    message = ''
    if request.method == 'POST':
        form = MemberJoinUsForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            phone_country = form.cleaned_data['phone_country']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            city = form.cleaned_data['city']
            country = form.cleaned_data['country']
            is_authorize = form.cleaned_data['is_authorize']
            
            mail_html = render_to_string(
                'member_panel/pages/joinus_mail.html', 
                {
                    'logo_url': 'https://qiprojects.in/static/admin_panel/assetss/images/icons/logo/ttclubmaillogo.png',
                    'full_name': full_name,
                    'phone_country': phone_country,
                    'phone_number': phone_number,
                    'email': email,
                    'city': city,
                    'country': country,
                    'is_authorize': is_authorize,
                 }
                )
            # print(mail_html)
            mail_message = strip_tags(mail_html)
            send_email("TTCLUB Member-Join Request Details",settings.EMAIL_HOST_USER,mail_message,mail_html)
            send_email("TTCLUB Member-Join Request Details",email,mail_message,mail_html)

            response_data = {
                "status": "true",
                "title": "Successful",
                "message": "Your membership request has been sent",
                'redirect': 'true',
                "redirect_url": reverse('web:member_index')
            }
            status_code = status.HTTP_200_OK
        else:
            message = generate_member_form_errors(form, formset=False)
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "message": message,
            }
            
        return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")


@member_login_required
@role_required(['member'])
def member_logout(request):
    logout(request)

    return redirect(reverse('web:member_login'))


def check_user_password(request):
    password = request.POST.get("password")
    user = User.objects.get(username=request.user.username)
    is_correct = user.check_password(password)
    
    if is_correct:
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": "true",
            "title": "Successful",
            "message": "password currect",
            "redirect": "true",
            "redirect_url": reverse('web:profile'),
        }
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": "false",
            "message": "Incorrect password",
        }
    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")

