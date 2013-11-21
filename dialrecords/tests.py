# coding=utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import json

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class RecordMissedCallsTest(TestCase):
    def test_record_a_new_missed_call(self):
        """
        Record a new missed call.
        One new record should be inserted into DB.
        """
        url = "/dialrecords/missedcalls/"
        called_number = "008618664565400"
        calling_number = "008618664565402"
        calling_date = "2013-10-25T06:30:59Z"
        data = {"called_number": called_number, "calling_number": calling_number, "calling_date": calling_date}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        # Fetch this record from DB
        url = "/dialrecords/missedcalls/" + called_number +"/"
        response = self.client.get(url)
        record_list = json.loads(response.content)
        self.assertEqual(called_number, record_list[-1]["called_number"])
        self.assertEqual(calling_number, record_list[-1]["calling_number"])
        self.assertEqual(calling_date, record_list[-1]["calling_date"])

    def test_record_multiple_new_missed_call(self):
        """
        Record multiple new missed calls.
        Multiple new record should be inserted into DB.
        """
        times = 9
        url = "/dialrecords/missedcalls/"
        called_number = "008618664565400"
        calling_number = "008618664565402"
        calling_date = "2013-10-25T06:30:59Z"
        data = {"called_number": called_number, "calling_number": calling_number, "calling_date": calling_date}
        for i in range(0,times):
            self.client.post(url, data)
        url = "/dialrecords/missedcalls/" + called_number +"/badge/"
        response = self.client.get(url)
        self.assertEqual(response.content, str(times))
        url = "/dialrecords/missedcalls/" + called_number +"/"
        response = self.client.get(url)
        record_list = json.loads(response.content)
        self.assertEqual(len(record_list), times)

    def test_delete_records(self):
        """
        When user has fetched missed calls, they should delete them in DB.
        Test whether fetched records has been deleted.
        """
        url = "/dialrecords/missedcalls/"
        called_number = "008618664565400"
        calling_number = "008618664565402"
        calling_date = "2013-10-25T06:30:59Z"
        data = {"called_number": called_number, "calling_number": calling_number, "calling_date": calling_date}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        url = "/dialrecords/missedcalls/" + called_number +"/badge/"
        response = self.client.get(url)
        self.assertEqual(response.content, '1')
        url = "/dialrecords/missedcalls/" + called_number + "/"
        self.client.delete(url)
        response = self.client.get(url)
        self.assertEqual(response.content, '[]')
        url = "/dialrecords/missedcalls/" + called_number +"/badge/"
        response = self.client.get(url)
        self.assertEqual(response.content, '0')