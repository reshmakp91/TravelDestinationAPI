from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from destinationapp.models import *
from destinationapp.serializers import *
from destinationapp.forms import *
from django.contrib.sessions.models import Session
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.middleware.csrf import get_token
from django.conf import settings
from django.urls import reverse
import requests
from django.contrib.auth import get_user_model


User = get_user_model()


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class StateListView(generics.ListAPIView):
    serializer_class = StateSerializer

    def get_queryset(self):
        country_id = self.kwargs['country_id']
        return State.objects.filter(country_id=country_id)

class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        state_id = self.kwargs['state_id']
        return District.objects.filter(state_id=state_id)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully.", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        print(f"Request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            print(f"Authenticated User: {user.username}, Token: {token.key}, Created: {created}")
            request.session['auth_token'] = str(token.key)
            request.session.modified = True
            print(f"Token stored in session: {token.key}")
            return Response({"token": token.key, "message": "Login successful."}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)  # Log the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)

class DestinationListView(generics.ListCreateAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            if isinstance(user, CustomUser):
                serializer.save(created_by=user)
            else:
                raise PermissionDenied("User is not a valid CustomUser instance.")
        else:
            raise PermissionDenied("You must be logged in to create a destination.")

class DestinationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]

def user_register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                api_url = 'http://127.0.0.1:8000/register/'
                data = {
                    'name': form.cleaned_data['name'],
                    'email': form.cleaned_data['email'],
                    'username': form.cleaned_data['username'],
                    'password': form.cleaned_data['password'],
                    'confirm_password': form.cleaned_data['confirm_password'],  # Ensure this is sent
                    'country': form.cleaned_data['country'].id,
                    'state': form.cleaned_data['state'].id,
                    'district': form.cleaned_data['district'].id
                }
                response = requests.post(api_url, data=data)
                if response.status_code == 201:
                    messages.success(request, 'Registration successful!')
                    return redirect('user_login')
                else:
                    messages.error(request, f'Error! {response.json()}')
            except requests.RequestException as e:
                messages.error(request, f'Error during API request: {str(e)}')
        else:
            messages.error(request, 'Invalid Form')
    country_id = request.POST.get('country')
    state_id = request.POST.get('state')
    if country_id:
        form.fields['state'].queryset = State.objects.filter(country_id=country_id)
    else:
        form.fields['state'].queryset = State.objects.none()

    if state_id:
        form.fields['district'].queryset = District.objects.filter(state_id=state_id)
    else:
        form.fields['district'].queryset = District.objects.none()
    return render(request, 'register.html', {'form': form})


def user_login(request):

    if request.method == 'POST':
        try:
            api_url = 'http://127.0.0.1:8000/login/'
            data = {
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'csrfmiddlewaretoken': get_token(request),  # Add CSRF token here
            }
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_json = response.json()
                token = response_json.get('token')
                if token:
                    request.session['auth_token'] = token
                    request.session.modified = True
                    messages.success(request, 'Login successful!')
                    return redirect('index')
                else:
                    messages.error(request, 'Login failed: Token not found.')
            else:
                error_message = response.json().get('detail', 'Please try again.')
                messages.error(request, f'Error! {error_message}')
        except requests.RequestException as e:
            messages.error(request, f'Error during API request: {str(e)}')

    return render(request, 'login.html')



def index(request):
    token = request.session.get('auth_token')
    if not token:
        messages.error(request, "You must be logged in to view destinations.")
        return redirect('user_login')
    try:
        token_obj = Token.objects.get(key=token)
        request.user = token_obj.user
    except Token.DoesNotExist:
        messages.error(request, "Invalid token. Please log in again.")
        return redirect('user_login')
    api_url = 'http://127.0.0.1:8000/destinations/'
    headers = {
        'Authorization': f'Token {token}',
        'X-CSRFToken': get_token(request),
    }
    try:
        response = requests.get(api_url, headers=headers)
        print(f"API Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            paginator = Paginator(data, 3)
            page = request.GET.get('page', 1)
            try:
                destinations = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                destinations = paginator.page(paginator.num_pages)
            is_owners = []
            user_id = request.user.id if request.user.is_authenticated else None
            for destination in destinations:
                created_by = destination.get('created_by')
                if isinstance(created_by, dict):
                    created_by = created_by.get('id')
                is_owners.append(created_by == user_id)
            context = {'destinations': destinations, 'is_owners': is_owners}
            return render(request, 'index.html', context)
        else:
            return render(request, 'index.html', {'error_message': f'Error: {response.status_code}'})
    except requests.RequestException as e:
        return render(request, 'index.html', {'error_message': f'Error: {str(e)}'})



def create_destination(request):
    if not request.session.get('auth_token'):
        messages.error(request, "You must be logged in to create a destination.")
        return redirect('user_login')

    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            api_url = f'http://127.0.0.1:8000/destinations/'
            token = request.session.get('auth_token')
            headers = {
                'Authorization': f'Token {token}',
                'X-CSRFToken': get_token(request),
            }
            files = {'Destination_img': form.cleaned_data['Destination_img']} if form.cleaned_data['Destination_img'] else None
            data = {
                'place_name': form.cleaned_data['place_name'],
                'weather': form.cleaned_data['weather'],
                'state': form.cleaned_data['state'],
                'district': form.cleaned_data['district'],
                'google_map_link': form.cleaned_data['google_map_link'],
                'description': form.cleaned_data['description'],
             }
            response = requests.post(api_url, data=data, files=files, headers=headers)
            if response.status_code == 201:
                messages.success(request, "Destination created successfully!")
                return redirect('index')
            else:
                messages.error(request, "Failed to create destination. Please try again.")
    else:
        form = DestinationForm()
    return render(request, 'create_destinations.html', {'form': form})


def detail_destination(request, pk):
    if not request.session.get('auth_token'):
        messages.error(request, "You must be logged in to view the destination.")
        return redirect('user_login')
    api_url = f'http://127.0.0.1:8000/destinations/{pk}/'
    token = request.session.get('auth_token')
    try:
        token_obj = Token.objects.get(key=token)
        request.user = token_obj.user
    except Token.DoesNotExist:
        messages.error(request, "Invalid token. Please log in again.")
        return redirect('user_login')
    headers = {
        'Authorization': f'Token {token}',
        'X-CSRFToken': get_token(request),
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Destination Data: {data}")
        created_by = data.get('created_by')
        print(f"Created By (raw): {created_by}")
        if isinstance(created_by, dict):
            created_by = created_by.get('id')

        user_id = request.user.id if request.user.is_authenticated else None
        print(f"Created By: {created_by}, User ID: {user_id}")
        is_owner = (created_by == user_id)
        print(f"is_owner: {is_owner}")
        return render(request, 'detail.html', {'destination': data, 'is_owner': is_owner})
    else:
        return render(request, 'detail.html', {'error_message': f'Error: {response.status_code}'})


def update_destination(request, pk):

    if not request.session.get('auth_token'):
        messages.error(request, "You must be logged in to create a destination.")
        return redirect('user_login')
    destination = get_object_or_404(Destination, id=pk)
    if request.method == 'POST':
        place_name = request.POST.get('place_name')
        weather = request.POST.get('weather')
        state = request.POST.get('state')
        district = request.POST.get('district')
        Destination_img = request.FILES.get('Destination_img')
        description = request.POST.get('description')
        google_map_link = request.POST.get('google_map_link')

        api_url = f'http://127.0.0.1:8000/destinations/{pk}/'
        token = request.session.get('auth_token')
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
        except Token.DoesNotExist:
            messages.error(request, "Invalid token. Please log in again.")
            return redirect('user_login')
        headers = {
            'Authorization': f'Token {token}',
            'X-CSRFToken': get_token(request),
        }

        data = {
            'place_name': place_name,
            'weather': weather,
            'state': state,
            'district': district,
            'description': description,
            'google_map_link': google_map_link,
        }

        files = {'Destination_img': Destination_img} if Destination_img else None

        try:
            response = requests.put(api_url, data=data, files=files, headers=headers)
            if response.status_code == 200:
                messages.success(request, 'Destination updated successfully.')
                return redirect(reverse('detail_destinations', kwargs={'pk': pk}))
            else:
                messages.error(request, f'Error submitting Destination {response.status_code}')
        except requests.RequestException as e:
            messages.error(request, f'Error during API request: {str(e)}')
    form = DestinationForm(instance=destination)
    return render(request, 'update_destination.html', {'form': form})

def delete_destination(request,id):

    if not request.session.get('auth_token'):
        messages.error(request, "You must be logged in to create a destination.")
        return redirect('user_login')
    destination = get_object_or_404(Destination, id=id)
    api_url = f'http://127.0.0.1:8000/destinations/{id}/'
    token = request.session.get('auth_token')
    try:
        token_obj = Token.objects.get(key=token)
        request.user = token_obj.user
    except Token.DoesNotExist:
        messages.error(request, "Invalid token. Please log in again.")
        return redirect('user_login')
    headers = {
        'Authorization': f'Token {token}',
        'X-CSRFToken': get_token(request),
    }
    response = requests.delete(api_url, headers=headers)
    print(f"Delete Response: {response.status_code}")
    if response.status_code == 200:
        print(f'Item with id {id} has been deleted')
        return redirect('home')
    else:
        print(f'Failed to delete item {response.status_code}')
    return redirect('index')

def base(request):
    return render(request,'base_home.html')


def logout(request):
    token = request.session.get('auth_token')

    if not token:
        messages.error(request, "You are not logged in.")
        return redirect('user_login')

    api_url = 'http://127.0.0.1:8000/logout/'  # Assume you have a logout API endpoint
    headers = {
        'Authorization': f'Token {token}',
        'X-CSRFToken': get_token(request),
    }
    try:
        response = requests.post(api_url, headers=headers)  # Use POST or DELETE based on your API
        if response.status_code == 200:
            request.session.flush()  # Clear session data
            messages.success(request, 'You have been logged out successfully.')
        else:
            messages.error(request, 'Failed to log out. Please try again.')
    except requests.RequestException as e:
        messages.error(request, f'Error during logout request: {str(e)}')

    return redirect('home')




