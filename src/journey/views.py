from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Car, Group, Journey
from .serializers import LocationSerializer
from .services import (clean_system, request_available_car,
                       get_available_group, process_cars_payload,
                       process_journey_payload)


class StatusAPIView(APIView):
    """
    GET status of the system
    """
    permission_classes = ()

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class CarAPIView(APIView):
    """
    PUT to add new cars
    """
    permission_classes = ()

    def put(self, request):
        cars = process_cars_payload(request.data)
        clean_system()

        try:
            Car.objects.bulk_create(cars)
        except Exception:
            raise SuspiciousOperation("Incorrect field in payload")

        return Response(status=status.HTTP_200_OK)


class JourneyAPIView(APIView):
    """
    POST a new request of a journey
    """
    permission_classes = ()

    def post(self, request):
        group = process_journey_payload(request.data)
        if Group.objects.filter(id=group.id).exists():
            raise SuspiciousOperation("Incorrect field in payload")

        try:
            group.save()
        except Exception:
            raise SuspiciousOperation("Incorrect field in payload")

        request_available_car(group)
        return Response(status=status.HTTP_200_OK)


class DropOffAPIView(APIView):
    """
    POST drop off a group
    """
    permission_classes = ()

    def post(self, request):
        group_id = request.GET.get('id')
        if not group_id.isdigit():
            raise SuspiciousOperation("Incorrect group id")

        group = get_object_or_404(Group, id=group_id)
        group.finish_journey()

        if hasattr(group, 'journey'):
            get_available_group(group.journey.car)
        return Response(status=status.HTTP_200_OK)


class LocateAPIView(APIView):
    """
    POST to locate a group in a car
    """
    permission_classes = ()

    def post(self, request):
        group_id = request.GET.get('id')
        if not group_id.isdigit():
            raise SuspiciousOperation("Incorrect group id")

        group = get_object_or_404(Group, id=group_id)

        if group.is_in_car():
            location = {
                'group': group.id,
                'car': group.get_car().id
            }

            return Response(
                LocationSerializer(location).data,
                status=status.HTTP_200_OK
            )
        elif group.is_already_drop_off():
            raise Http404

        return Response(status=status.HTTP_204_NO_CONTENT)
