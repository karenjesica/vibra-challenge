#!/usr/bin/env python
import unittest

from app import create_app, db
from app.config import Config
from app.models import Table


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_table(self):
        t = Table(id=1, hash="abc")
        db.session.add(t)
        db.session.commit()
        t = Table.query.filter_by(id=1).scalar()
        self.assertEqual(t.hash, "abc")


class CSVSearchTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.expected_response = [
            ["352", "Glen", "Rosebotham", "grosebotham9r@examiner.com", "Bigender", "Buzzster", "Romorantin-Lanthenay"],
            ["363", "Glendon", "Riche", "grichea2@joomla.org", "Bigender", "Fivechat", "Serhetabat"],
            ["713", "Glendon", "Iacomelli", "giacomellijs@drupal.org", "Non-binary", "Tazzy", "Nouakchott"]
        ]

    def tearDown(self):
        self.app_context.pop()

    def test_search_csv_should_return_200(self):
        # retrieving all records
        response = self.app.test_client().get("/search-csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["csv_result"]), 1000)

        # filtering by name
        response = self.app.test_client().get("/search-csv?name=glen")
        expected_response = self.expected_response.copy()
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.get_json()["csv_result"], expected_response)

        # filtering by city
        response = self.app.test_client().get("/search-csv?city=Lanthenay")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.get_json()["csv_result"], [expected_response[0]])

        # filtering by city and name
        response = self.app.test_client().get("/search-csv?name=glen&city=he")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.get_json()["csv_result"], [expected_response[0], expected_response[1]])

        # filtering by city, name and quantity
        response = self.app.test_client().get("/search-csv?name=glen&city=he&quantity=1")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.get_json()["csv_result"], [expected_response[0]])

        # no results found
        response = self.app.test_client().get("/search-csv?name=glen&city=not_exists&quantity=1")
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.get_json()["csv_result"], [])
