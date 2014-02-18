import requests
import oauth2 as oauth
import urlparse
import ipdb as ipdb
import re
import angellist
reload(angellist)
import urllib2
from progressbar import *

#######################################################################################
# Scrapes AngelList for Upenn alumni.							                      #
#                                                                                     #
# Author: Troy Shu                                                                    #
# Email : tmshu1@gmail.com                                                            #
# Web: http://www.troyshu.com                                                         #
#                                                                                     #
#######################################################################################


class AngellistQuakerBot:
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
		startups = []
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
				startups.append(startup['name'])
				

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
		
		
		return startupUrls, startups
		
	def _scrapeStartupPageForFounder(self, startupUrl):
		response = urllib2.urlopen(startupUrl)
		page_source = response.read()
		lines = page_source.split('\n')
		founderLine = ''
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

	def _getFounderPageFromName(self, founderName):
		#search angellist for foundername
		results = self.al.getSearch(self.al.access_token, query = founderName)
		
		#get first result's page
		return results[0][0]['url']


	def _getFounders(self, startupUrls):
		founderNames = []
		print 'scraping founder names...'
		pbar = ProgressBar(maxval=len(startupUrls))
		pbar.start()
		#get startup page
		count = 0
		for startupUrl in startupUrls:
			#scrape founder pages from startup page
			founderName = self._scrapeStartupPageForFounder(startupUrl)
			if founderName:
				founderNames.append(founderName)
			
			count+=1
			pbar.update(count)
		
		pbar.finish()

		#for each founder name, search, grab id
		print 'getting founder page for each founder...'
		pbar = ProgressBar(maxval=len(founderNames))
		pbar.start()
		count = 0
		founderPages = []
		for founderName in founderNames:
			founderPage = self._getFounderPageFromName(founderName)
			founderPages.append(founderPage)
			count+=1
			pbar.update(count)
		pbar.finish()

		return founderPages, founderNames 


	def _scrapePageForCollegeTag(self, founderPage):
		response = urllib2.urlopen(founderPage)
		page_source = response.read()
		lines = page_source.split('\n')
		for line in lines:
			if 'college-tag' in line:
				try:
					college = re.findall(r'college\-tag\"><a href=.*>(.*)</a>',line)[0]
					if college:
						return college
					else:
						return None
				except:
					return None
	
	def _isPennAlumni(self, inputText):
		inputText = inputText.lower()
		if 'penn' in inputText and 'penn state' not in inputText:
			return True
		else:
			return False

	def _isAlumni(self, inputText, school):
		#checks if given input text tells us if is alumni of school
		if school=='Penn':
			return self._isPennAlumni(inputText)
		else:
			raise Exception('alumni checking method for school %s not implemented yet' % school)


	def _checkCollegeTag(self, school, founderPage):
		#scrape founder page for college tag, compare
		college = self._scrapePageForCollegeTag(founderPage)
		#if we found a college tag
		if college:
			isAlumni = self._isAlumni(college, school)
			return isAlumni
		else:
			return None
		
	def 

	def _getIsAlumniFromPage(self, school, foundersAndPages):
		
		founderIsAlumni = {}
		for founder, founderPage in foundersAndPages:
			#check if college tag matches
			isAlmaMaterAngellist = self._checkCollegeTag(school, founderPage)
			
			if isAlmaMaterAngellist==None:
				#check linkedin
				isAlmaMaterLinkedin = self._checkLinkedinAlmaMater(school, founderPage)
				ipdb.set_trace()
			else:
				founderIsAlumni[founder] = isAlmaMaterAngellist

		ipdb.set_trace()
		return founderIsAlumni

	def findFounderAlumni(self, city='NYC', school='Penn', topPct = 0.10, followMin = None):
		#get all startups in city
		startupUrls, startupNames = self._findStartups(city, topPct, followMin)

		#get founders of each startup
		founderPages, founders = self._getFounders(startupUrls)

		#for each founder, find out if belong to input school: first angellist tag, then linkedin
		isAlumni = self._getIsAlumniFromPage(school, zip(founders, founderPages))

		
	
