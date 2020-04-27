from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_reg_page),
    path('create_user', views.create_user),
    path('login',views.login),
    path('logout', views.logout),
    path('dashboard', views.dashboard_page),
    path('trips/new', views.add_trip_page),
    path('trips/create', views.create_trip),
    path('trips/<int:trip_id>', views.view_trip_page),
    path('trips/<int:trip_id>/join', views.join_trip),
    path('trips/<int:trip_id>/cancel', views.cancel_trip),
    path('trips/<int:trip_id>/edit', views.edit_trip_page),
    path('trips/<int:trip_id>/update', views.update_trip),
    path('trips/<int:trip_id>/delete', views.delete_trip),
]