from rest_framework.serializers import Serializer, IntegerField


class LocationSerializer(Serializer):
    group = IntegerField()
    car = IntegerField()
