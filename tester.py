import angellistquakerbot
reload(angellistquakerbot)
from angellistquakerbot import AngellistQuakerBot

bot = AngellistQuakerBot()
bot.findFounderAlumni(followMin = 10000)