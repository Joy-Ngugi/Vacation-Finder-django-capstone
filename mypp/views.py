from rest_framework import status, views, generics, permissions, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, SignupSerializer, UserSerializer, PlaceSerializer, EventSerializer, BookingSerializer, TravelTipSerializer, ItinerarySerializer, BookmarkSerializer, RatingSerializer
from .models import User, Place, Event, Booking, TravelTip, Itinerary, Bookmark, Rating
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
import requests
import json
import os
from dotenv import load_dotenv
# from .mpesa_utils import get_access_token
from django.http import JsonResponse
import requests
import base64
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
# from .mpesa_payment import lipa_na_mpesa
import stripe
import openrouteservice


class CustomRefreshToken(RefreshToken):
    def __init__(self, user):
        super().__init__()
        self.payload['role'] = user.role  


def get_tokens_for_user(user):
    refresh = CustomRefreshToken(user)
    return {
        'access': str(refresh.access_token),  
        'refresh': str(refresh),  
    }



def authenticate_with_email(email, password):
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        return None
    


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    
    user = authenticate_with_email(email, password)
    if user:
        
        role = user.role  
        
        if role == 'admin':
            
            print('Admin login successful')
        elif role == 'user':
            
            print('User login successful')
        
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)  
        
        return Response({
            "access_token": access_token,  
            "role": role,                  
            "message": "Login successful"
        }, status=200)
    
    
    return Response({"error": "Invalid credentials"}, status=401)
    


@api_view(['POST'])
def signup(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.role = 'traveller'
    user.save()

    return Response({"message": "User registered successfully!"}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def promote_to_admin(request):
    if not request.user.is_staff:  
        return Response({"error": "Unauthorized"}, status=403)

    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        user.role = 'admin'  
        user.save()
        return Response({"message": f"User {email} promoted to admin!"}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    
class UserListView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all() 
        serializer = UserSerializer(users, many=True)  
        return Response(serializer.data)


class UserProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    


class PlaceListCreateAPIView(APIView):
    """
    Handles GET (list all places) and POST (create a new place).
    """
    def get(self, request):
        places = Place.objects.all()
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceDetailAPIView(APIView):
    """
    Handles GET, PUT, and DELETE for a specific place by ID.
    """
    def get(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        serializer = PlaceSerializer(place)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        serializer = PlaceSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    
class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class TravelTipListView(generics.ListAPIView):
    queryset = TravelTip.objects.all()
    serializer_class = TravelTipSerializer


class ItineraryCreateView(generics.CreateAPIView):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
def create_booking(request):
    data = request.data
    try:
        user = User.objects.get(id=data['user'])
        place = Place.objects.get(id=data['place'])
        booking = Booking.objects.create(
            user=user,
            place=place,
            check_in=data['check_in'],
            check_out=data['check_out'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=data['email'],
            adults=data['adults'],
            children=data['children'],
            trip_preferences=data.get('trip_preferences', '')
        )
        print(f"Booking created: {booking}")
        
        send_mail(
                "Thank you for booking",
                f"Dear {booking.first_name},\n\nYour booking has been received at Safiri Central Kenya and is being processed. We will get back to you in 24 hrs. Thank you for choosing us!",
                "joyngugi559@gmail.com",
                [booking.email],
                fail_silently=False,
                # from_email='Safiri Central Kenya <joyngugi559@gmail.com>',
            )
        
        return Response({"message": "Booking successful!  A confirmation email has been sent."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
 

            
@api_view(['GET'])
def get_all_bookings(request):
    bookings = Booking.objects.all()
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(["PATCH"])
def update_booking_status(request, booking_id):
    try:
        
        booking = Booking.objects.get(id=booking_id)
        
        
        new_status = request.data.get("status")
        
        if new_status:
            
            booking.status = new_status
            booking.save()

            
            if new_status == "Confirmed":
                subject = "Booking Status Update"
                message = f"Dear {booking.first_name},\n\nYour booking status is now confirmed at Safiri Central Kenya. Your stay is from {booking.check_in} to {booking.check_out}. Thank you for choosing us!"
            elif new_status == "Cancelled":
                subject = "Booking Status Update"
                message = f"Dear {booking.first_name},\n\nWe regret to inform you that your booking has been cancelled. If you need further assistance, feel free to reach out."
            else:
                
                subject = "Booking Status Update"
                message = f"Dear {booking.first_name},\n\nYour booking status is now {new_status} at Safiri Central Kenya. Your stay is from {booking.check_in} to {booking.check_out}. Thank you for choosing us!"

            
            send_mail(
                subject,
                message,
                "Safiri Central Kenya <joyngugi559@gmail.com>",  
                [booking.email],
                fail_silently=False,
            )
            
            return Response({"message": "Booking status updated successfully"}, status=200)
        
        return Response({"error": "Invalid status"}, status=400)
    
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)
    

stripe.api_key = "sk_test_51Qo6xj07eTs0A6VxMWJNSOTBk9FXRUf91UV8UN0KexLSc6GAFYwxiqRI4WwwhoWyvU4k00BIS69FYEWIYuZpYcAs00Q53f0DfN"

@csrf_exempt
def create_checkout_session(request):
    try:
        
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=400)
        
        # data = json.loads(request.body.decode("utf-8"))   # Ensure you're getting the booking details
        # booking_id = data.get("booking_id")  # Ensure the frontend sends the booking ID
        
        # if not booking_id:
        #     return JsonResponse({"error": "Missing booking_id"}, status=400)

        # # 🔹 Retrieve booking details
        # try:
        #     booking = Booking.objects.get(id=booking_id)
        # except Booking.DoesNotExist:
        #     return JsonResponse({"error": "Booking not found"}, status=404)
        
             
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Booking',
                    },
                    'unit_amount': 200, 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
            
        )
        
        

        return JsonResponse({'sessionId': checkout_session.id})  # ✅ Always return response

    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=500)  # ✅ Handle Stripe errors

    except Exception as e:
        return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500) 
    
          
# @csrf_exempt  # Disable CSRF protection for webhooks
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = "whsec_776a95adbc68bc3a95615b1e91cc22fea02cf3f16c369aec84ecb6b11e0999ce"

#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

#         # Check if event is checkout session completed
#         if event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             booking_id = session.get("metadata", {}).get("booking_id")
            
#             if booking_id:
#                 try:
#                     booking = Booking.objects.get(id=booking_id)
#                     email = booking.email 

            
#                     send_mail(
#                         "Payment Received - Thank You!",
#                         f"Dear Customer,\n\nYour payment has been successfully received. Thank you for booking with us!",
#                         "joyngugi559@gmail.com",
#                         [email],
#                         fail_silently=False,
#                     )

#                     return JsonResponse({'message': 'Email sent successfully'}, status=200)
#                 except Booking.DoesNotExist:
#                     return JsonResponse({'error': 'Booking not found'}, status=404)

#     except stripe.error.SignatureVerificationError as e:
#         return JsonResponse({'error': 'Webhook signature verification failed'}, status=400)

#     except Exception as e:
#         return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500)

#     return JsonResponse({'message': 'Webhook received'}, status=200)


class BookmarkPlaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        place = get_object_or_404(Place, id=id)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, place=place)

        if created:
            return Response({"message": "Place bookmarked successfully"}, status=status.HTTP_201_CREATED)
        else:
            bookmark.delete()
            return Response({"message": "Bookmark removed"}, status=status.HTTP_200_OK)

class BookmarkListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        bookmarks = Bookmark.objects.filter(user_id=user_id)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)
    
class RatePlaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        place = get_object_or_404(Place, id=id)
        rating_value = request.data.get("rating")

        if not (1 <= rating_value <= 5):
            return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            user=request.user, place=place,
            defaults={"rating": rating_value}
        )
        return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)

class UserBookmarksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, place_id=None):
        print("Authorization Header:", request.headers.get("Authorization"))
        print(f"Authenticated User: {request.user}") 
        
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=401)
        
        bookmarks = Bookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, place_id=None):
        """Bookmark a place"""
        if not place_id:
            return Response({"error": "Missing place ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            place = Place.objects.get(id=place_id)
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, place=place)
            if not created:
                return Response({"message": "Already bookmarked"}, status=400)
            return Response({"message": "Place bookmarked!"}, status=201)
        except Place.DoesNotExist:
            return Response({"error": "Place not found"}, status=404)

    def delete(self, request, place_id=None):
        """Remove a bookmark"""
        if not place_id:
            return Response({"error": "Missing place ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        bookmark = Bookmark.objects.filter(user=request.user, place_id=place_id)
        if bookmark.exists():
            bookmark.delete()
            return Response({"message": "Bookmark removed!"}, status=200)
        return Response({"error": "Bookmark not found"}, status=404)

    
class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """
    Returns a list of places the user has bookmarked.
    """
    user = request.user
    bookmarks = Bookmark.objects.filter(user=user).select_related('place')
    places = [bookmark.place for bookmark in bookmarks]  # Extract places
    serializer = PlaceSerializer(places, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookings(request):
    print(f"Request received from user: {request.user}")
    user = request.user
    print(f"Authenticated user: {user.username}")
    bookings = Booking.objects.filter(user=user).select_related("place") 
    print(f"Bookings found: {bookings}")
    
    if bookings.count() == 0:
        print("No bookings found")
        return Response([], status=200)
    
    serializer = BookingSerializer(bookings, many=True)  
    return Response(serializer.data)

class BulkBookingDeleteView(APIView):
    def delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No booking IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bookings = Booking.objects.filter(id__in=ids)
            bookings.delete()
            return Response({"message": "Bookings deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
  
