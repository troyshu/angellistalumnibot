import requests
import oauth2 as oauth
import urlparse
import ipdb as ipdb
import re
import angellist
reload(angellist)
from werkzeug.urls import *
import urllib2

#######################################################################################
# Scrapes AngelList for Upenn alumni.							                      #
#                                                                                     #
# Author: Troy Shu                                                                    #
# Email : tmshu1@gmail.com                                                            #
# Web: http://www.troyshu.com                                                         #
#                                                                                     #
#######################################################################################


class AngelistQuakerBot:
	def __init__(self):
		self.al = angellist.AngelList()
		self.al.access_token = '436c4e00aa39c52f0c04e68a5373d407'

		self.locationTagIdMap = {
			'NYC':1664,
			'SV':1681
		}


	def _findStartups(self, city, topPct, followMin):
		print 'getting all startups in %s:' % city

		getLocationId = self.locationTagIdMap[city]

		#get all startups in city
		startupUrls = []
		pageCount = 1
		count = 0
		perPage = 50
		stop = False
		while not stop:
			print 'getting page %s of startups...' % (pageCount)

			#get most popular startups first
			search_response = self.al.getTagsStartups(self.al.access_token, getLocationId, order='popularity', per_page = perPage, page=pageCount)

			#extract all startup urls
			startups = search_response['startups']

			for startup in startups:
				#if start up is hidden, continue
				if startup['hidden']:
					continue

				startupUrls.append(startup['angellist_url'])

				

				#if we've reached a min follower count, break
				if followMin and int(startup['follower_count'])<followMin:
					print 'reached min follower count of %s' % followMin
					stop = True
					break


			count += perPage
			#if we reached the end
			if count >= int(search_response['total']):
				print 'reached the end of AngelList startups for %s' % city
				stop = True
			#if we reached more than topPct of most popular startups (by followers)
			if count > topPct*float(search_response['total']):
				print 'finished grabbing top %s of startups by follower count' % topPct
				stop = True


			pageCount += 1
		
		return startupUrls
		
	def _scrapeStartupPageForFounder(self, startupUrl):
		response = urllib2.urlopen(startupUrl)
		page_source = response.read()
		lines = page_source.split('\n')
		#hacky: use regex to scrape founder's name
		for lineCount in range(0,len(lines)):
			line = lines[lineCount]
			if '<meta content=\'FOUNDER\'' in line:
				founderLine = lines[lineCount+1]
				break
		if founderLine:
			founderName = re.findall(r'<meta content=\'(.*)\' name=',founderLine)[0]
			return founderName
		else:
			return None

	def _getFounders(self, startupUrls):
		founderNames = []
		#get startup page
		for startupUrl in startupUrls:
			#scrape founder pages from startup page
			founderName = self._scrapeStartupPageForFounder(startupUrl)
			if founderName:
				founderNames.append(founderName)

		ipdb.set_trace()
		#for each founder name, search, grab id


	def findFounderAlumni(self, city='NYC', school='Penn', topPct = 0.10, followMin = None):
		#get all startups in city
		startupUrls = self._findStartups(city, topPct, followMin)

		#get founders of each startup
		founders = self._getFounders(startupUrls)

		#for each founder, find out if graduated from school



		
	
