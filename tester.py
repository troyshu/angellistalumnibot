import angellistquakerbot
reload(angellistquakerbot)
from angellistquakerbot import AngellistQuakerBot
import ipdb as ipdb

bot = AngellistQuakerBot()

rez = bot.findFounderAlumni(followMin = 1000)

ipdb.set_trace()


