angellistalumnibot
==================

A class that scrapes AngelList for all startups given an input city (e.g. NYC), then scrapes the founder of each startup, then checks AngelList or LinkedIn to see whether founder is alumni of input school (e.g. Univeristy of Pennsylvania). 

#Usage
```python
from angellistalumnibot import AngellistAlumniBot
bot = AngellistAlumniBot()
rez = bot.findFounderAlumni(city'NYC', school='Penn', topPct=0.10, followMin = 20)
```

rez now contains a DataFrame where the columns are founder name, startup name, and a boolean of whether founder belongs to input school.

#Notes
Currently only supports two cities, NYC and SF, and one school, Penn. Implementing the methods to support other cities and schools is pretty straightforward!

The scraper/bot is also very slow, probably because it's making so many HTTP requests. An improvement for the future.