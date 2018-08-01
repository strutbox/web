from django import template
from django.utils.html import mark_safe
from rapidjson import Encoder

register = template.Library()


class HTMLSafeEncoder(Encoder):
    def __call__(self, obj, stream=None, *, chunk_size=65536):
        rv = super().__call__(obj, stream=stream, chunk_size=chunk_size)
        rv = rv.replace("&", "\\u0026")
        rv = rv.replace("<", "\\u003c")
        rv = rv.replace(">", "\\u003e")
        rv = rv.replace("'", "\\u0027")
        return rv


htmlsafe_encoder = HTMLSafeEncoder()


@register.filter(name="serialize")
def serialize(value):
    return mark_safe(htmlsafe_encoder(value))
