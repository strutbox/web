from django import template
from django.utils.html import _json_script_escapes, mark_safe
from rapidjson import Encoder

register = template.Library()


class HTMLSafeEncoder(Encoder):
    def __call__(self, obj, stream=None, *, chunk_size=65536):
        return (
            super()
            .__call__(obj, stream=stream, chunk_size=chunk_size)
            .translate(_json_script_escapes)
        )


htmlsafe_encoder = HTMLSafeEncoder()


@register.filter(name="serialize")
def serialize(value):
    return mark_safe(htmlsafe_encoder(value))


@register.filter(name="json_script")
def json_script(value, element_id):
    return mark_safe(
        f'<script id="{element_id}" type="application/json">{mark_safe(htmlsafe_encoder(value))}</script>'
    )
