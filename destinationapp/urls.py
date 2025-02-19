from django.urls import path
from destinationapp import views
from .views import UserRegistrationView, UserLoginView, DestinationListView, DestinationDetailView, CountryListView, StateListView, DistrictListView, LogoutView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='registration'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('destinations/', DestinationListView.as_view(), name='destination-list'),
    path('destinations/<int:pk>/', DestinationDetailView.as_view(), name='destination-detail'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('states/<int:country_id>/', StateListView.as_view(), name='state-list'),
    path('districts/<int:state_id>/', DistrictListView.as_view(), name='district-list'),
    path('logout/', LogoutView.as_view(), name='logout_view'),

    path('register_user/', views.user_register, name='user_register'),
    path('login_user/', views.user_login, name='user_login'),
    path('index/', views.index, name='index'),
    path('create/', views.create_destination, name='create_destinations'),
    path('detail/<int:pk>/', views.detail_destination, name='detail_destinations'),
    path('update/<int:pk>/',views.update_destination, name='update_destination'),
    path('delete/<int:id>/', views.delete_destination, name='delete_destination'),
    path('', views.base, name='home'),
    path('user_logout/',views.logout, name='logout')
]
