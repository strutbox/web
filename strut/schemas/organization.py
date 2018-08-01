from marshmallow import Schema, fields


class OrganizationSchema(Schema):
    name = fields.Str()
    slug = fields.Str()
    # settings = fields.Dict()
    # date_created = fields.DateTime()


class OrganizationMemberSchema(Schema):
    organization = fields.Nested(OrganizationSchema)
    date_joined = fields.DateTime()
