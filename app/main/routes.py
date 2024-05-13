import csv
from apiflask import APIBlueprint as Blueprint
from flask.views import MethodView
from app.serializers import SearchCSVSerializer
from flask import current_app as app
from flask import jsonify
from flask import request
from sqlalchemy.exc import IntegrityError

from app import db
from app.errors.handlers import error_response
from app.models import Table

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return jsonify(hello="scaffold")


@bp.route("/log")
def log():
    app.logger.debug("This is a debug log, you can only see it when app.debug is True")
    app.logger.info("Some info")
    app.logger.warn("Warning")
    app.logger.error("Something was broken")
    return jsonify(log="ok")


@bp.route("/redis/<key>", methods=["GET"])
def get_redis_value(key):
    v = app.redis.get(key) or b""
    return jsonify(result=v.decode())


@bp.route("/redis/<key>/<value>", methods=["PUT"])
def set_redis_value(key, value):
    return jsonify(set=app.redis.set(key, value))


@bp.route("/db/<hash>", methods=["PUT"])
def set_hash(hash):
    t = Table(hash=hash)
    db.session.add(t)

    try:
        db.session.commit()
        result = True
    except IntegrityError as e:
        app.logger.error(e)
        result = False

    return jsonify(result=result)


@bp.route("/db/<int:id>", methods=["GET"])
def get_hash(id):
    t = Table.query.filter_by(id=id).scalar()
    return jsonify(hash=t.hash if t else "")


@bp.route("/error/<int:code>")
def error(code):
    app.logger.error(f"Error: {code}")
    return error_response(code)


@bp.route("/search-csv", methods=["GET"])
class SearchCSVView(MethodView):
    log_prefix = "[CSV Search]"
    def get(self, *args, **kwargs):
        try:
            schema = SearchCSVSerializer()
            csv_data = schema.load(request.args)
            name = csv_data.get("name", "")
            city = csv_data.get("city", "")
            quantity = csv_data.get("quantity", "")


            results = []
            with open("app/files/vibra_challenge.csv", newline="") as csvfile:
                reader = csv.reader(csvfile)

                app.logger.info(f"{self.log_prefix} Name filter: {name}." if name else f"{self.log_prefix} No filter applied for name.")
                app.logger.info(f"{self.log_prefix} City filter: {city}." if city else f"{self.log_prefix} No filter applied for city.")
                for row in reader:
                    name_match = not name or name.lower() in row[1].lower()
                    city_match = not city or city.lower() in row[-1].lower()
                    if name_match and city_match:
                        results.append(row)

                if quantity:
                    results = results[:quantity]

            app.logger.info(f"{self.log_prefix} Listing {len(results)} results.")
            return jsonify({'csv_result': results}), 200
        except Exception as e:  # NOQA
            app.logger.error(f"Error: {e}")
            return error_response(500, message=str(e))
