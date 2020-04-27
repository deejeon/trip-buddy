from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt

from .models import User, Trip

def login_reg_page(request):
    return render(request, 'login_reg.html')

def create_user(request):
    potential_users = User.objects.filter(email = request.POST['email'])

    if len(potential_users) != 0:
        messages.error(request, "User with that email already exists!")
        return redirect('/')

    errors = User.objects.basic_validator(request.POST)

    if len(errors) > 0:
        for key, val in errors.items():
            messages.error(request, val)
        return redirect('/')

    hashed_pw = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()

    new_user = User.objects.create(
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        email = request.POST['email'],
        password = hashed_pw,
    )

    request.session['user_id'] = new_user.id

    return redirect('/dashboard')

def login(request):
    potential_users = User.objects.filter(email = request.POST['email'])

    if len(potential_users) == 0:
        messages.error(request, "Please check your email and password.")
        return redirect('/')

    user = potential_users[0]

    if not bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        messages.error(request, "Please check your email and password.")
        return redirect('/')

    request.session['user_id'] = user.id

    return redirect('/dashboard')

def logout(request):
    if 'user_id' not in request.session:
        messages.error(request, "You are not logged in!")
        return redirect('/')

    request.session.clear()

    return redirect('/')

def dashboard_page(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')
        
    current_user = User.objects.get(id=request.session['user_id'])
    current_user_added_trips = current_user.added_trips.all()
    current_user_created_trips = current_user.created_trips.all()
    other_trips = Trip.objects.exclude(id__in = current_user_added_trips).exclude(id__in = current_user_created_trips)

    context = {
        'current_user': current_user,
        'current_user_added_trips': current_user_added_trips,
        'current_user_created_trips': current_user_created_trips,
        'other_trips': other_trips
    }

    return render(request, 'dashboard.html', context)

def add_trip_page(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')
        
    current_user = User.objects.get(id=request.session['user_id'])

    context = {
        'current_user': current_user,
    }

    return render(request, 'add_trip.html', context)

def create_trip(request):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])

    trip_errors = Trip.objects.basic_validator(request.POST)

    if len(trip_errors) > 0:
        for key, val in trip_errors.items():
            messages.error(request, val)
        return redirect('/trips/new')

    new_trip = Trip.objects.create(
        destination = request.POST['destination'],
        start_date = request.POST['start_date'],
        end_date = request.POST['end_date'],
        plan = request.POST['plan'],
        created_by_user = current_user,
    )

    return redirect('/dashboard')

def view_trip_page(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)

    current_trip_added_users = current_trip.added_users.all()

    added_empty = True

    if len(current_trip_added_users) > 0:
        added_empty = False

    context = {
        'current_user': current_user,
        'current_trip': current_trip,
        'current_trip_added_users': current_trip_added_users,
        'added_empty': added_empty
    }

    return render(request, 'view_trip.html', context)

def join_trip(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)

    current_user.added_trips.add(current_trip)

    return redirect('/dashboard')

def cancel_trip(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)

    current_user.added_trips.remove(current_trip)

    return redirect('/dashboard')

def edit_trip_page(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id = request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)
    current_trip.start_date = current_trip.start_date.strftime('%Y-%m-%d')
    current_trip.end_date = current_trip.end_date.strftime('%Y-%m-%d')

    if current_trip.created_by_user != current_user:
        messages.error(request, "You have not created this trip. You cannot edit it!")
        return redirect('/dashboard')

    context = {
        "current_user": current_user,
        "current_trip": current_trip,
    }

    return render(request, 'edit_trip.html', context)

def update_trip(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)

    if current_trip.created_by_user != current_user:
        messages.error(request, "You have not created this trip. You cannot edit it!")
        return redirect('/dashboard')

    trip_errors = Trip.objects.basic_validator(request.POST)

    if len(trip_errors) > 0:
        for key, val in trip_errors.items():
            messages.error(request, val)
        return redirect(f'/trips/{trip_id}/edit')

    current_trip.destination = request.POST['destination']
    current_trip.start_date = request.POST['start_date']
    current_trip.end_date = request.POST['end_date']
    current_trip.plan = request.POST['plan']
    current_trip.save()

    return redirect('/dashboard')

def delete_trip(request, trip_id):
    if 'user_id' not in request.session:
        messages.error(request, "Must be logged in!")
        return redirect('/')

    current_user = User.objects.get(id=request.session['user_id'])
    current_trip = Trip.objects.get(id = trip_id)

    if current_trip.created_by_user != current_user:
        messages.error(request, "You have not created this trip. You cannot remove it!")
        return redirect('/dashboard')

    current_trip.delete()

    return redirect('/dashboard')