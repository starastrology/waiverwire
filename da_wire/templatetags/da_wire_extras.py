from da_wire.models import MLBAffiliate

from django import template

register = template.Library()

@register.simple_tag
def get_affiliate(level, mlbteam):
    if level != "Rk":
        return MLBAffiliate.objects.filter(level__level=level, mlbteam=mlbteam).first()
    else:
        return MLBAffiliate.objects.filter(level__level="MLB", mlbteam=mlbteam).first()
