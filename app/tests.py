import asyncio
import unittest
from json import dumps
from unittest.mock import ANY, patch

from app import create_app, db
from app.config import Config
from app.helpers import load_csv_data
from app.models import Table
from app.tasks import process_search_csv


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ModelsTest(BaseTestCase):
    def test_table(self):
        t = Table(id=1, hash="abc")
        db.session.add(t)
        db.session.commit()
        t = Table.query.filter_by(id=1).scalar()
        self.assertEqual(t.hash, "abc")


class CSVSearchTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        load_csv_data("app/files/vibra_challenge.csv")
        self.client = self.app.test_client()
        self.expected_data_csv = [
            {
                "id": 352,
                "user_id": 352,
                "first_name": "Glen",
                "last_name": "Rosebotham",
                "email": "grosebotham9r@examiner.com",
                "gender": "Bigender",
                "company": "Buzzster",
                "city": "Romorantin-Lanthenay",
            },
            {
                "id": 363,
                "user_id": 363,
                "first_name": "Glendon",
                "last_name": "Riche",
                "email": "grichea2@joomla.org",
                "gender": "Bigender",
                "company": "Fivechat",
                "city": "Serhetabat",
            },
            {
                "id": 713,
                "user_id": 713,
                "first_name": "Glendon",
                "last_name": "Iacomelli",
                "email": "giacomellijs@drupal.org",
                "gender": "Non-binary",
                "company": "Tazzy",
                "city": "Nouakchott",
            },
        ]
        self.expected_url = "http://localhost:5000/redis/transaction_id"

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
    def test_search_csv_should_return_202(self, mock_process_search_csv):
        response = self.app.test_client().get("/search-csv?name=glen")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()["message"], "Search request received")
        mock_process_search_csv.assert_called_once_with("glen", "", "", ANY)

    @patch("app.main.routes.process_search_csv")
    def test_search_csv_should_return_400(self, mock_process_search_csv):
        response = self.app.test_client().get("/search-csv?not_exists=glen")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "{'not_exists': ['Unknown field.']}")
        mock_process_search_csv.assert_not_called()
