import json

from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import authentication_classes, \
    permission_classes
from rest_framework.generics import CreateAPIView

from . import serializers
from .models import Account, Profile
from .permissions import UpdateOwnAccount


class AccountViewset(viewsets.ModelViewSet):
    """Handles creating, reading and updating account """

    serializer_class = serializers.AccountSerializer
    queryset = Account.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (UpdateOwnAccount,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email', 'timezone')


class LoginViewset(viewsets.ViewSet):
    """check username and password and return authtoken """

    serializer_class = AuthTokenSerializer

    def create(self, request):
        return ObtainAuthToken().post(request)


class AuthVerifyView(APIView):
    serializer_class = serializers.AuthSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, formar=None):
        print(request.user.username)
        return Response({'verify': True})

    # def post(self, request, ):
    #     serializer = serializers.AuthSerializer(data=request.data)
    #     if serializer.is_valid():
    #         username = serializer.data.get('username')
    #         password = serializer.data.get('password')
    #
    #         try:
    #             user = Account.objects.get(username=username)
    #             if user.check_password(raw_password=password):
    #                 """Return accesstoken"""
    #                 print('true')
    #             else:
    #                 """Return HTTP_400"""
    #                 return Response({"message": "Authentication failed"},
    #                                 status=status.HTTP_400_BAD_REQUEST)
    #         except:
    #             return Response({"message": "Authentication failed"},
    #                             status=status.HTTP_400_BAD_REQUEST)
    #     return Response({'username': username, 'password': password})


class AuthMEView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, formar=None):
        acc = Account.objects.get(username=request.user.username)
        user_infor = {
            'id': str(acc.uuid),
            'username': acc.username,
            'email': acc.email,
            'timezone': acc.timezone,
            'profile': 'null'
        }
        return Response(user_infor, content_type='application/json')


@authentication_classes([])
@permission_classes([])
class AccountCreateView(APIView):
    serializer_class = serializers.AccountSerializer

    def post(self, request):
        serializer = serializers.AccountSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            email = serializer.data.get('email')
            acc = Account()
            acc.username = username
            acc.password = password
            acc.email = email
            acc.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        acc = Account.objects.get(username=request.user.username)
        print(acc)
        acc.delete()
        return Response(status=status.HTTP_200_OK)

class UpdateEmailView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serializer = serializers.UpdateEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            acc = Account.objects.get(username=request.user.username)
            acc.email = email
            acc.save()
            return Response(status= status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        acc = Account.objects.get(username=request.user.username)
        try:
            prof = Profile.objects.get(uuid=acc.uuid)
            msg = {
                'id': prof.id,
                'uuid':prof.uuid,
                'fullname':prof.fullname,
                'address':prof.address,
                'country':prof.country,
                'phone': prof.phone,
                'date_of_birth':prof.date_of_birth
            }
            return Response(msg, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Profile not found'},
                            status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request):
        serializer = serializers.UpdateProfileSerializer(data=request.data)
        if serializer.is_valid():
            fullname = serializer.data.get('fullname')
            address = serializer.data.get('address')
            country = serializer.data.get('country')
            phone = serializer.data.get('phone')
            date_of_birth = serializer.data.get('date_of_birth')

            acc = Account.objects.get(username = request.user.username)
            profiles = Profile.objects.all()

            if str(acc.uuid) in [profile.uuid for profile in profiles]:
                prof = profiles.get(uuid=acc.uuid)
                if fullname != '':
                    prof.fullname = fullname
                if address != '':
                    prof.address = address
                if country != '':
                    prof.country = country
                if phone != '':
                    prof.phone = phone
                if date_of_birth != '':
                    print(date_of_birth)
                    prof.date_of_birth = date_of_birth
                prof.save()
                return Response(status= status.HTTP_200_OK)
            else:
                prof = Profile()
                prof.uuid = acc.uuid
                prof.fullname = fullname
                prof.address = address
                prof.country = country
                prof.phone = phone
                prof.date_of_birth = date_of_birth
                prof.save()
                return Response(status=status.HTTP_200_OK)


        else:
            return Response(serializer.errors,
                            status = status.HTTP_400_BAD_REQUEST)