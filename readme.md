AngelListAlumniBot
==================

A class that scrapes AngelList for all startups given an input city (e.g. NYC), then scrapes the founder of each startup, then checks AngelList or LinkedIn to see whether founder is alumni of input school (e.g. Univeristy of Pennsylvania). 

#Usage
```python
from angellistalumnibot import AngellistAlumniBot
bot = AngellistAlumniBot()
rez = bot.findFounderAlumni(city='NYC', school='Penn', topPct=0.10, followMin = 20)
```


- **city**: defined in a dict that maps name (e.g. NYC) to an AngelList location id. See AngelList API for more info
- **school**: string for target school/college
- **topPct**: startups are retrieved from AngelList in order of descending popularity, topPct is the top fraction of startups that you want to actually keep. This is a way to filter out rando startups
- **followMin**: the minimum number of AngelList followers a startup must have to be included in the search. Another way to filter out rando startups


rez now contains a DataFrame where the columns are founder name, startup name, and a boolean of whether founder belongs to input school.

#Notes
Currently only supports two cities, NYC and SV (Silicon Valley), and one school, Penn. Implementing the methods to support other cities and schools is pretty straightforward!

The scraper/bot is also very slow, probably because it's making so many HTTP requests. An area of improvement for the future.