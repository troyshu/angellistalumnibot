import angelistquakerbot
reload(angelistquakerbot)
from angelistquakerbot import AngelistQuakerBot

bot = AngelistQuakerBot()
bot._findStartups(followMin = 700)