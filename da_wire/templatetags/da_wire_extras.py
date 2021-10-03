from da_wire.models import MLBAffiliate

from django import template
import urllib.parse

register = template.Library()

@register.simple_tag
def get_affiliate(level, mlbteam):
    return MLBAffiliate.objects.filter(level__level=level, mlbteam=mlbteam).first()

@register.filter
def replace_forward_slash(value):
    return urllib.parse.quote(value, safe='')
