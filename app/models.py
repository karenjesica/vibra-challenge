from typing import Any

from app import db

Model: Any = db.Model


class Table(Model):
    __tablename__ = "table"
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), unique=True, nullable=False)


class CSVData(Model):
    __tablename__ = "csv_data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    company = db.Column(db.String(100))
    city = db.Column(db.String(100))

    def __repr__(self):
        return f"<CSVData id={self.id}, user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, gender={self.gender}, company={self.company}, city={self.city}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "gender": self.gender,
            "company": self.company,
            "city": self.city
        }
