from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('book/', views.search_results, name='search_results'),
    path('get-location/', views.fetch_real_time_location, name='fetch_real_time_location'),
    path('fare/', lambda request: views.render(request, 'fare.html'), name='fare_page'),
    path('book-tickets/<int:option_id>/', views.book_tickets, name='book_tickets')

]



