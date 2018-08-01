from marshmallow import Schema, fields


class UserSchema(Schema):
    email = fields.Str()
