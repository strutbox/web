from marshmallow import Schema, fields


class SongMetaSchema(Schema):
    source = fields.Int()
    identifier = fields.Str()
    title = fields.Function(lambda obj: obj.resolver.title)
    thumbnail = fields.Function(lambda obj: obj.resolver.thumbnail)
    duration = fields.Function(lambda obj: obj.resolver.duration)
    date_created = fields.DateTime()
    last_synced = fields.DateTime()


class SongSchema(Schema):
    id = fields.Int()
    start = fields.Int()
    length = fields.Int()
    date_created = fields.DateTime()
    meta = fields.Nested(SongMetaSchema)
    file = fields.Function(
        lambda obj: None if not obj.file_id else obj.file.get_public_url()
    )


class SongJobSchema(Schema):
    song = fields.Nested(SongSchema)
    status = fields.Int()
    log = fields.String()
    date_created = fields.DateTime()
    date_updated = fields.DateTime()


class PlaylistSchema(Schema):
    identifier = fields.String()
    owner = fields.Nested("UserSchema")
    shared = fields.Bool()
    songs = fields.Nested(SongSchema, many=True)


class PlaylistSubscriptionSchema(Schema):
    playlist = fields.Nested(PlaylistSchema)
    is_active = fields.Bool()
    date_created = fields.DateTime()
