from da_wire.models import MLBAffiliate

from django import template
import urllib.parse

register = template.Library()

@register.simple_tag
def get_affiliate(level, mlbteam):
    return MLBAffiliate.objects.filter(level=level, mlbteam=mlbteam).first()

@register.filter
def replace_forward_slash(value):
    return urllib.parse.quote(value, safe='')

@register.simple_tag
def is_pro(user):
    if user.is_authenticated:
        try:
            if user.prouser:
                return True
            else:
                return False
        except:
            return False
    else:
        return False

@register.filter
def remove_zero(value):
    if str(value)[0] == "0":
        return str(value)[1:]
    else:
        return value

@register.simple_tag
def get_thangy(team):
    return team
