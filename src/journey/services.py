from django.core.exceptions import SuspiciousOperation

from .models import Car, Group


def process_cars_payload(data):
    """
    Process payload for cars requests

    :param data: Data with cars ids and seats
    :type data: dict

    :returns: List of cars
    :type returns: [journey.Car]
    """
    cars = []
    for car in data:
        if (
            'id' in car and
            'seats' in car and
            isinstance(car['id'], int) and
            isinstance(car['seats'], int)
        ):
            cars.append(Car(id=car['id'], seats=car['seats']))
            check_capacity(int(car['seats']))
        else:
            raise SuspiciousOperation('Incorrect payload')
    return cars


def process_journey_payload(data):
    """
    Process payload for journey requests

    :param data: Data with a journey id and people
    :type data: dict

    :returns: Group
    :type returns: journey.Group
    """
    if (
        'id' in data and
        'people' in data and
        isinstance(data['id'], int) and
        isinstance(data['people'], int)
    ):
        check_capacity(int(data['people']))
        return Group(id=data['id'], people=data['people'])
    raise SuspiciousOperation('Incorrect payload')


def check_capacity(value):
    """
    Check capacity of cars and groups

    :param data: Value of capacity
    :type data: int
    """
    if value > 6 or value < 4:
        raise SuspiciousOperation("Incorrect capacity")


def clean_system():
    """
    Restart system to the initial status
    """
    Car.objects.all().delete()
    Group.objects.all().delete()


def request_available_car(group):
    """
    Detect and, if is possible, assign a car for a group

    :param group: Group that wants a car
    :type group: journey.Group

    :returns: Car assigned if is possible, None if isn't
    :type returns: journey.Car
    """
    car = group.get_available_car()
    if car:
        group.assign_car(car)
    return car


def get_available_group(car):
    """
    Detect and, if is possible, assign a group to a car

    :param car: Available car that wants a group
    :type car: journey.Car

    :returns: Group assigned if is possible, None if isn't
    :type returns: journey.Group
    """
    group = car.get_available_group()
    if group:
        group.assign_car(car)
    return group
