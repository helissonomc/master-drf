from multiprocessing import context
from authors_api.settings.local import DEFAULT_FROM_EMAIL
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from core_apps.users import serializers
from .exceptions import CantFollowYourself, NotYourProfile
from .models import Profile
from .pagination import ProfilePagination
from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer
from .serializers import ProfileSerializer, FollowingSerializer, UpdateProfileSerializer


User = get_user_model()

# """
# FBV
# """
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def get_all_profiles(request):
#     """
#     Get all profiles
#     """
#     profiles = Profile.objects.all()
#     serializer = ProfileSerializer(profiles, many=True)
#     namespaced_response = {'profiles': serializer.data}
#     return Response(namespaced_response, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def get_profile_detail(request, username):
#     try:
#         profile = Profile.objects.get(user__username=username)
#     except Profile.DoesNotExist:
#         raise NotFound('Profile not found')

#     serializer = ProfileSerializer(profile)
#     namespaced_response = {'profile': serializer.data}
#     return Response(namespaced_response, status=status.HTTP_200_OK)

"""
CBV
"""
class ProfileListAPIView(generics.ListAPIView):
    """
    Get all profiles
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfilesJSONRenderer]
    pagination_class = ProfilePagination


class ProfileDetailAPIView(generics.RetrieveAPIView):
    """
    Get Detail profile
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]
    pagination_class = ProfilePagination

    def retrieve(self, request, *args, **kwargs):
        try:
            profile = self.queryset.get(user__username=kwargs['username'])
        except Profile.DoesNotExist:
            raise NotFound('Profile not found')

        serializer = self.serializer_class(profile, context={'request': request})
        namespaced_response = {'profile': serializer.data}

        return Response(namespaced_response, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    """
    Update profile
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]
    pagination_class = ProfilePagination

    def patch(self, request, username):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('Profile not found')

        user_name = request.user.username
        if user_name != username:
            raise NotYourProfile('You can only update your own profile')

        data = request.data
        serializer = self.serializer_class(instance=request.user.profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_my_followers(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        raise NotFound('Profile not found')

    serializer = FollowingSerializer(profile.followers_list(), many=True)
    namespaced_response = {
        'followers': serializer.data,
        'num_of_followers': len(serializer.data)
    }
    return Response(namespaced_response, status=status.HTTP_200_OK)


class FollowUnfollowAPIView(generics.GenericAPIView):
    """
    Follow or unfollow a user
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('Profile not found')

        my_following_list = profile.following_list()
        serializer = ProfileSerializer(my_following_list, many=True, context={'request': request})
        formatted_response = {
            'status_code': status.HTTP_200_OK,
            'users_i_follow': serializer.data,
            'num_of_users_i_follow': len(serializer.data)
        }

        return Response(formatted_response, status=status.HTTP_200_OK)

    def post(self, request, username):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('Profile not found')

        user_name = request.user.username
        if user_name == username:
            raise CantFollowYourself('You can not follow yourself')


        current_user_profile = request.user.profile

        if profile in current_user_profile.following_list():
            formatted_response = {
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'You are already following this user'
            }
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

        current_user_profile.follow(profile)

        subject = 'A new user followed you'
        message = '{} just followed you'.format(user_name)

        from_email = DEFAULT_FROM_EMAIL
        recipient_list = [profile.user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)

        formatted_response = {
            'status_code': status.HTTP_200_OK,
            'message': 'You are now following {}'.format(username)
        }
        return Response(formatted_response, status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('Profile not found')

        user_name = request.user.username
        if user_name == username:
            raise CantFollowYourself('You can not unfollow yourself')

        current_user_profile = request.user.profile

        if profile not in current_user_profile.following_list():
            formatted_response = {
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'You are not following this user'
            }
            return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

        current_user_profile.unfollow(profile)

        formatted_response = {
            'status_code': status.HTTP_200_OK,
            'message': 'You are no longer following {}'.format(username)
        }
        return Response(formatted_response, status=status.HTTP_200_OK)