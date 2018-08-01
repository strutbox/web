from django.db.models import Model as BaseModel

__all__ = ("sane_repr", "Model")


def r(thing):
    if callable(thing):
        thing = thing()
    if isinstance(thing, memoryview):
        thing = bytes(thing)
    if isinstance(thing, bytes):
        thing = thing.hex()
    return repr(thing)


def sane_repr(*attrs):
    def _repr(self):
        pairs = ", ".join(f"{a}={r(getattr(self, a, None))}" for a in attrs)

        return f"<{type(self).__name__} at {hex(id(self))}: {pairs}>"

    return _repr


class Model(BaseModel):
    class Meta:
        abstract = True

    __repr__ = sane_repr("id")
