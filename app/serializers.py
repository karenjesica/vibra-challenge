from marshmallow import Schema, fields


class SearchCSVSerializer(Schema):
    name = fields.String()
    city = fields.String()
    quantity = fields.Integer()
