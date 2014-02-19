import angellistalumnibot
reload(angellistalumnibot)
from angellistalumnibot import AngellistAlumniBot
import ipdb as ipdb

bot = AngellistAlumniBot()

rez = bot.findFounderAlumni(followMin = 2000)

ipdb.set_trace()


