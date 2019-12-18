from model_mommy import mommy

from django.test import TestCase
from django.utils import timezone

from ..exceptions import AssignCarException, JourneyException
from ..models import Car, Group, Journey


class CarTestCase(TestCase):
    """
    Tests for car model methods
    """
    def setUp(self):
        self.seats = 4
        self.incorrect_seats = 5
        self.car = mommy.make('journey.car', seats=self.seats)

    def test_get_available_group(self):
        """Get group valid"""
        group_ok = mommy.make('journey.group', people=self.seats)
        mommy.make('journey.group', people=self.seats)
        self.assertEqual(self.car.get_available_group(), group_ok)

    def test_get_second_available_group(self):
        """Get group first in order is incorrect"""
        mommy.make('journey.group', people=self.incorrect_seats)
        group_ok = mommy.make('journey.group', people=self.seats)
        self.assertEqual(self.car.get_available_group(), group_ok)

    def test_get_available_group_not_exist(self):
        """Get group and not exist"""
        mommy.make('journey.group', people=self.incorrect_seats)
        self.assertIsNone(self.car.get_available_group())

    def test_get_available_group_without_availables(self):
        """Get group without available cars"""
        mommy.make('journey.group', people=self.seats, is_available=False)
        self.assertIsNone(self.car.get_available_group())

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()


class GroupTestCase(TestCase):
    """
    Tests for group model methods
    """
    def setUp(self):
        self.people = 4
        self.incorrect_people = 5
        self.group = mommy.make('journey.group', people=self.people)

    def test_get_car(self):
        """Get the car valid"""
        self.group.is_available = False
        self.group.save()
        mommy.make('journey.car', seats=self.people)
        car = mommy.make('journey.car', seats=self.people, is_available=False)
        mommy.make('journey.journey', car=car, group=self.group)
        self.assertEqual(self.group.get_car(), car)

    def test_get_car_without_journey(self):
        """Get the car but It doesn't have journey"""
        self.assertIsNone(self.group.get_car())

    def test_get_available_car(self):
        """Get available car valid"""
        car_ok = mommy.make('journey.car', seats=self.people)
        mommy.make('journey.car', seats=self.people)
        self.assertEqual(self.group.get_available_car(), car_ok)

    def test_get_second_available_car(self):
        """Get available car but it's the second """
        self.group.people = self.incorrect_people
        self.group.save()
        mommy.make('journey.car', seats=self.people)
        car_ok = mommy.make('journey.car', seats=self.incorrect_people)
        self.assertEqual(self.group.get_available_car(), car_ok)

    def test_get_available_car_not_exist(self):
        """Get available car but the seats are insuficient"""
        mommy.make('journey.car', seats=self.people)
        self.group.people = self.incorrect_people
        self.group.save()
        self.assertIsNone(self.group.get_available_car())

    def test_get_available_group_without_availables(self):
        """Get available car but not exists"""
        mommy.make('journey.car', seats=self.people, is_available=False)
        self.assertIsNone(self.group.get_available_car())

    def test_get_available_car_with_group_in_car(self):
        """Get available car but a group is using that car"""
        car = mommy.make('journey.car', seats=self.people, is_available=False)
        mommy.make('journey.journey', car=car, group=self.group)
        self.assertIsNone(self.group.get_available_car())

    def test_get_available_car_with_group_already_drop_off(self):
        """A group with finished journey try to drop off"""
        self.group.is_available = False
        self.group.save()
        car = mommy.make('journey.car', seats=self.people, is_available=True)
        mommy.make('journey.journey', car=car, group=self.group, finished=timezone.now())
        self.assertRaises(JourneyException, lambda: self.group.get_available_car())

    def test_assign_car(self):
        """Assign a car to a group valid"""
        car = mommy.make('journey.car', seats=self.people)
        self.group.assign_car(car)
        self.assertFalse(self.group.is_available)
        self.assertFalse(car.is_available)
        self.assertEqual(self.group.journey.car, car)
        self.assertIsNone(self.group.journey.finished)

    def test_assign_car_not_available_car(self):
        """Assign a car but the car is not available"""
        car = mommy.make('journey.car', seats=self.people, is_available=False)
        self.assertRaises(AssignCarException, lambda: self.group.assign_car(car))
        self.assertTrue(self.group.is_available)
        self.assertFalse(car.is_available)

    def test_assign_car_not_available_group(self):
        """Assign a car but the group is not available"""
        car = mommy.make('journey.car', seats=self.people)
        self.group.is_available = False
        self.group.save()
        self.assertRaises(AssignCarException, lambda: self.group.assign_car(car))
        self.assertFalse(self.group.is_available)
        self.assertTrue(car.is_available)

    def test_assign_car_more_people_than_seats(self):
        """Assign a car but people is than seats"""
        car = mommy.make('journey.car', seats=self.people)
        self.group.people = self.incorrect_people
        self.group.save()
        self.assertTrue(self.group.is_available)
        self.assertTrue(car.is_available)
        self.assertRaises(AssignCarException, lambda: self.group.assign_car(car))

    def test_assign_car_finished_journey(self):
        """Assign car to a group when the journey is finished"""
        car = mommy.make('journey.car', seats=self.people)
        self.group.assign_car(car)
        self.group.finish_journey()
        self.assertRaises(JourneyException, lambda: self.group.assign_car(car))
        self.assertFalse(self.group.is_available)
        self.assertTrue(car.is_available)

    def test_assign_car_with_group_in_car(self):
        """Assign car but a group is in the car"""
        car = mommy.make('journey.car', seats=self.people, is_available=False)
        mommy.make('journey.journey', car=car, group=self.group)
        self.assertRaises(AssignCarException, lambda: self.group.assign_car(car))

    def test_assign_car_with_group_already_drop_off(self):
        """Assign car but the journey of the group finished"""
        self.group.is_available = False
        self.group.save()
        car = mommy.make('journey.car', seats=self.people, is_available=True)
        mommy.make('journey.journey', car=car, group=self.group, finished=timezone.now())
        self.assertRaises(JourneyException, lambda: self.group.assign_car(car))

    def test_finish_journey(self):
        """Finish the journey of a group valid"""
        self.group.is_available = False
        self.group.save()
        car = mommy.make('journey.car', seats=self.people, is_available=False)
        journey = mommy.make('journey.journey', group=self.group, car=car)
        self.group.finish_journey()
        self.assertTrue(car.is_available)
        self.assertIsNotNone(journey.finished)

    def test_finish_journey_without_journey(self):
        """Try to finish a journey without a journey"""
        self.group.finish_journey()
        self.assertFalse(self.group.is_available)

    def test_finish_journey_canceling_journey(self):
        """Try to finish the journey previously cancelled"""
        self.group.finish_journey()
        self.assertFalse(self.group.is_available)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()


class JourneyTestCase(TestCase):
    """
    Tests for journey model methods 
    """
    def setUp(self):
        self.people = 4
        self.car = mommy.make('journey.car', seats=self.people)
        self.group = mommy.make('journey.group', people=self.people)
        self.journey = mommy.make('journey.journey', car=self.car, group=self.group)

    def test_finish(self):
        """Finish a journey valid"""
        self.journey.finish()
        self.assertIsNotNone(self.journey.finished)
        self.assertTrue(self.car.is_available)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()
