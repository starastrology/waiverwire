from da_wire.models import Player
import unicodedata

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

players = Player.objects.all()
for player in players:
    player.first_name_unaccented = strip_accents(player.first_name)
    player.last_name_unaccented = strip_accents(player.last_name)
    player.save()
