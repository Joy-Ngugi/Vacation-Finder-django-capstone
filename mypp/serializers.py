from rest_framework import serializers
from .models import User, Place, Event, Booking, TravelTip, Itinerary, Bookmark, Rating

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields =  '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    is_traveller = serializers.SerializerMethodField()
    bookmarks = PlaceSerializer(many=True, read_only=True, source="bookmark_set.place")

    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin', 'is_traveller', 'role', "bookmarks"]
        
    def get_is_admin(self, obj):
        return obj.role == 'admin'

    def get_is_traveller(self, obj):
        return obj.role == 'traveller'
        
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role=validated_data['role'] 
        )
        return user
    

    def validate_role(self, value):
        if value not in dict(User._meta.get_field('role').choices).keys():
            raise serializers.ValidationError("Invalid role selected.")
        return value


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields =  '__all__'
  
 
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        

class BookingSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        
class TravelTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTip
        fields = '__all__'

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'