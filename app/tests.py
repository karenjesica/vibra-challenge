#!/usr/bin/env python
import asyncio
import unittest
from json import dumps
from unittest.mock import ANY, patch

from app import create_app, db
from app.config import Config
from app.models import Table
from app.tasks import process_search_csv


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
        self.expected_data_csv = [
            [
                "352",
                "Glen",
                "Rosebotham",
                "grosebotham9r@examiner.com",
                "Bigender",
                "Buzzster",
                "Romorantin-Lanthenay",
            ],
            [
                "363",
                "Glendon",
                "Riche",
                "grichea2@joomla.org",
                "Bigender",
                "Fivechat",
                "Serhetabat",
            ],
            [
                "713",
                "Glendon",
                "Iacomelli",
                "giacomellijs@drupal.org",
                "Non-binary",
                "Tazzy",
                "Nouakchott",
            ],
        ]
        self.expected_url = "http://localhost:5000/redis/transaction_id"

    def tearDown(self):
        self.app_context.pop()

    def test_process_search_csv_filtering_by_name(self):
        name = "glen"
        city = ""
        quantity = ""
        results_json = dumps(self.expected_data_csv)
        with patch("urllib.request.urlopen"), patch(
            "urllib.request.Request"
        ) as mock_request:
            asyncio.run(process_search_csv(name, city, quantity, "transaction_id"))
            mock_request.assert_called_once_with(
                self.expected_url,
                data=results_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )

    def test_process_search_csv_filtering_by_city(self):
        name = ""
        city = "Lanthenay"
        quantity = ""
        results_json = dumps([self.expected_data_csv[0]])
        with patch("urllib.request.urlopen"), patch(
            "urllib.request.Request"
        ) as mock_request:
            asyncio.run(process_search_csv(name, city, quantity, "transaction_id"))
            mock_request.assert_called_once_with(
                self.expected_url,
                data=results_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )

    def test_process_search_csv_filtering_by_city_and_name(self):
        name = "glen"
        city = "he"
        quantity = ""
        results_json = dumps([self.expected_data_csv[0], self.expected_data_csv[1]])
        with patch("urllib.request.urlopen"), patch(
            "urllib.request.Request"
        ) as mock_request:
            asyncio.run(process_search_csv(name, city, quantity, "transaction_id"))
            mock_request.assert_called_once_with(
                self.expected_url,
                data=results_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )

    def test_process_search_csv_filtering_by_city_and_name_and_quantity(self):
        name = "glen"
        city = "he"
        quantity = 1
        results_json = dumps([self.expected_data_csv[0]])
        with patch("urllib.request.urlopen"), patch(
            "urllib.request.Request"
        ) as mock_request:
            asyncio.run(process_search_csv(name, city, quantity, "transaction_id"))
            mock_request.assert_called_once_with(
                self.expected_url,
                data=results_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )

    def test_process_search_csv_no_results_found(self):
        name = "glen"
        city = "not_exists"
        quantity = 1
        results_json = dumps([])
        with patch("urllib.request.urlopen"), patch(
            "urllib.request.Request"
        ) as mock_request:
            asyncio.run(process_search_csv(name, city, quantity, "transaction_id"))
            mock_request.assert_called_once_with(
                self.expected_url,
                data=results_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )

    @patch("app.main.routes.process_search_csv")
    def test_search_csv_should_return_200(self, mock_process_search_csv):
        response = self.app.test_client().get("/search-csv?name=glen")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()["message"], "Search request received")
        mock_process_search_csv.assert_called_once_with("glen", "", "", ANY)
