from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
import requests
from .models import TravelOption, Booking
from .forms import RegisterForm

# User Registration
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('fare_page')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# User Login
from django.contrib.auth import get_user_model

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next')  # Get 'next' parameter

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email instead of username
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)

                # Redirect user to intended page after login
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)

                return redirect('fare_page')  # Default redirect if no 'next' param
        except User.DoesNotExist:
            pass  # User does not exist, go to login page again

    return render(request, 'login.html', {'error': "Invalid email or password"})

# Logout View
def user_logout(request):
    logout(request)
    return redirect('home')

# Home Page
def home(request):
    travel_options = TravelOption.objects.all()
    return render(request, 'home.html', {'travel_options': travel_options})

# Search Results
def search_results(request):
    travel_options = TravelOption.objects.all()

    transport_type = request.GET.get("transport_type")
    source = request.GET.get("source")
    destination = request.GET.get("destination")
    date = request.GET.get("date")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    min_seats = request.GET.get("min_seats")

    if transport_type:
        travel_options = travel_options.filter(type=transport_type)
    if source:
        travel_options = travel_options.filter(source__icontains=source)
    if destination:
        travel_options = travel_options.filter(destination__icontains=destination)
    if date:
        travel_options = travel_options.filter(date_time__date=date)
    if min_price:
        travel_options = travel_options.filter(price__gte=min_price)
    if max_price:
        travel_options = travel_options.filter(price__lte=max_price)
    if min_seats:
        travel_options = travel_options.filter(available_seats__gte=min_seats)

    return render(request, "search_results.html", {"travel_options": travel_options})

# Booking View
@login_required
def book_tickets(request):
    option_id = request.GET.get('option_id')

    if not option_id:
        return redirect('search_results')  # Redirect if no option selected

    travel_option = get_object_or_404(TravelOption, pk=option_id)

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.travel_option = travel_option

            if booking.num_seats > travel_option.available_seats:
                return render(request, 'book_tickets.html', {
                    'error': "Not enough seats available!",
                    'travel_option': travel_option
                })

            # Deduct seats and save booking
            travel_option.available_seats -= booking.num_seats
            travel_option.save()

            booking.total_price = booking.num_seats * travel_option.price
            booking.save()

            return redirect('fare_page')  # Redirect after booking confirmation

    return render(request, 'book_tickets.html', {'travel_option': travel_option})

# Fetch Real-Time Location
def fetch_real_time_location(request):
    source = request.GET.get("source")
    if not source:
        return JsonResponse({"error": "Missing source parameter"}, status=400)
    
    api_url = f"https://nominatim.openstreetmap.org/search?format=json&q={source}"
    try:
        response = requests.get(api_url, headers={"User-Agent": "Django-App"})
        if response.status_code != 200:
            return JsonResponse({"error": "API Error"}, status=500)
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)

# Fare Page
@login_required
def fare_page(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'fare.html', {'bookings': bookings})
