import csv
from app import db
from app.models import CSVData

def load_csv_data(filename):
    with open(filename, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            csv_data = CSVData(
                user_id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                gender=row[4],
                company=row[5],
                city=row[6]
            )
            db.session.add(csv_data)
    db.session.commit()
