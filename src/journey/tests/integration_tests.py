from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.test import TransactionTestCase
from django.urls import reverse

from ..models import Car, Group, Journey


class GetStatusTest(APITestCase):
    """ Test module for GET status API """

    def setUp(self):
        self.url = reverse('get_status')

    def test_get_status_valid(self):
        """Get status valid"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PutCarsTest(TransactionTestCase):
    """ Test module for PUT cars API """
    client = APIClient

    def setUp(self):
        self.url = reverse('put_cars')

    def test_put_cars_valid(self):
        """Put cars valid"""
        payload = [
            {
                'id': 1,
                'seats': 4
            },
            {
                'id': 2,
                'seats': 6
            },
        ]
        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_cars_duplicate_id_invalid(self):
        """Put cars with same id"""
        payload = [
            {
                'id': 1,
                'seats': 4
            },
            {
                'id': 1,
                'seats': 6
            },
        ]

        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_cars_incorrect_id_invalid(self):
        """Put car with a string id"""
        payload = [
            {
                'id': "a",
                'seats': 4
            },
        ]

        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_cars_incorrect_seats_invalid(self):
        """Put cars with a string seats"""
        payload = [
            {
                'id': 1,
                'seats': "a"
            },
        ]

        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_cars_too_many_seats_invalid(self):
        """Put cars with too many seats"""
        payload = [
            {
                'id': 1,
                'seats': 7
            },
        ]

        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_cars_less_seats_invalid(self):
        """Put cars with less seats"""
        payload = [
            {
                'id': 1,
                'seats': 3
            },
        ]

        response = self.client.put(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()


class PostJourneyTest(TransactionTestCase):
    """ Test module for POST journey API """
    client = APIClient

    def setUp(self):
        self.url = reverse('post_journey')

    def test_post_journey_valid(self):
        """Post a journey valid"""
        payload = {
            'id': 1,
            'people': 4
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_journey_duplicate_id_invalid(self):
        """Post a journey with a duplicate id"""
        mommy.make('journey.group', id=1)
        payload = {
            'id': 1,
            'people': 4
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_journey_incorrect_id_invalid(self):
        """Post a journey with a string id"""
        payload = {
            'id': "a",
            'people': 4
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_journey_incorrect_seats_invalid(self):
        """Post a journey with a string people"""
        payload = {
            'id': 1,
            'people': "a"
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_journey_too_many_people_invalid(self):
        """Post a journey with too many people"""
        payload = {
            'id': 1,
            'seats': 7
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_journey_less_people_invalid(self):
        """Post a journey with less people"""
        payload = {
            'id': 1,
            'people': 3
        }

        response = self.client.post(self.url, data=payload, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()


class PostDropOffTest(TransactionTestCase):
    """ Test module for POST drop off API """
    client = APIClient

    def setUp(self):
        self.group = mommy.make('journey.group')
        self.url = "{}?id=".format(reverse('post_dropoff'))

    def test_post_dropoff_valid(self):
        """Post drop off invalid"""
        self.url = "{}{}".format(self.url, self.group.id)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_dropoff_incorrect_id_invalid(self):
        """Post drop off with not exists id"""
        self.url = "{}{}".format(self.url, self.group.id+1)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_dropoff_wrong_id_invalid(self):
        """Post drop off with wrong id"""
        self.url = "{}{}".format(self.url, "a")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()


class PostLocateTest(TransactionTestCase):
    """ Test module for POST locate API """
    client = APIClient

    def setUp(self):
        self.car = mommy.make('journey.car')
        self.group = mommy.make('journey.group')
        self.url = "{}?id=".format(reverse('post_locate'))

    def test_post_locate_valid(self):
        """Post to locate a group valid"""
        self.url = "{}{}".format(self.url, self.group.id)
        self.group.is_available = False
        self.group.save()
        self.car.is_available = False
        self.car.save()
        mommy.make('journey.journey', car=self.car, group=self.group)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_locate_group_without_car_invalid(self):
        """Post to locate a group without car"""
        self.url = "{}{}".format(self.url, self.group.id)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_locate_incorrect_id_invalid(self):
        """Post to locate a group with invalid id"""
        self.url = "{}{}".format(self.url, self.group.id+1)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_locate_wrong_id_invalid(self):
        """Post to locate a group with wrong id"""
        self.url = "{}{}".format(self.url, "a")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        Car.objects.all().delete()
        Group.objects.all().delete()
