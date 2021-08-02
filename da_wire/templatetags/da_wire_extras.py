from da_wire.models import MLBAffiliate

from django import template

register = template.Library()

@register.simple_tag
def get_affiliate(level, mlbteam):
    return MLBAffiliate.objects.filter(level__level=level, mlbteam=mlbteam).first()

