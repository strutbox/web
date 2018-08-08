from marshmallow import Schema, fields


class UserSettingsSchema(Schema):
    privacy_public = fields.Bool(default=False)


class UserSchema(Schema):
    email = fields.Str()


class DetailedUserSchema(UserSchema):
    settings = fields.Nested(UserSettingsSchema)
