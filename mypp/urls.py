from django.urls import path
from .views import  UserListView, UserProfileView,  PlaceListCreateAPIView, PlaceDetailAPIView, EventListView, BookingCreateView, TravelTipListView, ItineraryCreateView, create_booking, get_all_bookings, update_booking_status, create_checkout_session, BookmarkPlaceView, RatePlaceView, UserBookmarksView, UserBookingsView, user_bookmarks, user_bookings, BulkBookingDeleteView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('users/', UserListView.as_view(), name='login'),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('promote-to-admin/', views.promote_to_admin, name='promote_to_admin'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('places/', PlaceListCreateAPIView.as_view(), name='place-list-create'),
    path('places/<int:pk>/', PlaceDetailAPIView.as_view(), name='place-detail'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('tips/', TravelTipListView.as_view(), name='travel-tips'),
    path('itineraries/', ItineraryCreateView.as_view(), name='create-itinerary'),
    path('bookings/', create_booking, name="create-booking"),
    path('admin/bookings/', get_all_bookings, name='admin-bookings'),
    path("admin/bookings/<int:booking_id>/update/", update_booking_status, name="update-booking-status"),
    path('admin/bookings/bulk-delete/', BulkBookingDeleteView.as_view(), name='bulk-delete'),
    path("create-checkout-session/", create_checkout_session, name="checkout"),
    # path("stripe-webhook/", stripe_webhook, name="stripe-webhook"),
     path('places/<int:id>/bookmark/', BookmarkPlaceView.as_view(), name='bookmark-place'),
    path('places/<int:id>/rate/', RatePlaceView.as_view(), name='rate-place'),
    path('user/bookmarks/', user_bookmarks, name='user-bookmarks'),
    path('bookmarks/<int:place_id>/', UserBookmarksView.as_view(), name='user-bookmarks'),
    # path('bookings/', UserBookingsView.as_view(), name='user-bookings'),
    path('api/bookmarks/', views.BookmarkListView.as_view(), name='bookmarks-list'),
    path('user/bookings/', user_bookings, name="user-bookings"),
    # path('directions/', views.get_directions, name="get_directions"),
]