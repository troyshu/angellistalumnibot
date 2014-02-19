import requests
import oauth2 as oauth
import urlparse
import ipdb as ipdb
import re
import angellist
reload(angellist)
import urllib2
from progressbar import *
from pandas import DataFrame

#######################################################################################
# Scrapes AngelList for alumni.							                              #
#                                                                                     #
# Author: Troy Shu                                                                    #
# Email : tmshu1@gmail.com                                                            #
# Web: http://www.troyshu.com                                                         #
#                                                                                     #
#######################################################################################


class AngellistAlumniBot:
	def __init__(self):
		self.al = angellist.AngelList()
		#this is my access token. if you have your own access token, please use it
		self.al.access_token = '436c4e00aa39c52f0c04e68a5373d407'

		self.locationTagIdMap = {
			'NYC':1664,
			'SV':1681
		} #maps a city string to angellist id for that location


	def _findStartups(self, city, topPct, followMin):
		print 'getting all startups in %s:' % city

		getLocationId = self.locationTagIdMap[city]

		#get all startups in city
		startupUrls = []
		startupNames = []
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
				startupNames.append(startup['name'])
				

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
		
		
		return startupUrls, startupNames
		
	def _scrapeStartupPageForFounder(self, startupUrl):
		try:
			response = urllib2.urlopen(startupUrl)
			page_source = response.read()
		except:
			#for some reaosn, if the startup's page on angellist doesn't exist or something
			return None
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
		try:
			return results[0][0]['url']
		except:
			return None


	def _getFounders(self, startupUrls, startupNames):
		startupUrlAndNames = zip(startupUrls, startupNames)

		foundersAndStartups = {}
		print 'scraping founder names from AngelList startup pages...'
		pbar = ProgressBar(maxval=len(startupUrls))
		pbar.start()
		#get startup page
		count = 0
		for startupUrl, startupName in startupUrlAndNames:
			#scrape founder pages from startup page
			founderName = self._scrapeStartupPageForFounder(startupUrl)
			if founderName:
				foundersAndStartups[founderName] = startupName
			count+=1
			pbar.update(count)
		
		pbar.finish()


		#for each founder name, search, grab id
		print 'getting AngelList founder page for each founder...'
		pbar = ProgressBar(maxval=len(foundersAndStartups.keys()))
		pbar.start()
		count = 0
		foundersAndPages = {}
		for founderName in foundersAndStartups.keys():
			founderPage = self._getFounderPageFromName(founderName)
			count+=1
			pbar.update(count)

			if not founderPage == None:
				foundersAndPages[founderName] = founderPage

			else:
				continue

		pbar.finish()

		return foundersAndPages, foundersAndStartups 


	def _scrapePageForCollegeTag(self, founderPage):
		try:
			response = urllib2.urlopen(founderPage)
			page_source = response.read()
		except:
			#for some reason, if the person's angellist page doesn't exist or something
			return None
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
	
	def _getLinkedInUrl(self, founderPage):
		#get linked in page from angellist founder page
		try:
			response = urllib2.urlopen(founderPage)
			page_source = response.read()
		except:
			#for some reason, if the person's angellist page doesn't exist
			return None
		lines = page_source.split('\n')
		linkedinUrl = ''
		for line in lines:
			if 'linked_in-link' in line:
				try:
					linkedinUrl = re.findall(r'<a href=\"(.*)\" class=\"linked_in\-link\"',line)[0]
					
					if linkedinUrl:
						return linkedinUrl
					else:
						return None
				except:
					return None
		
		return None

	def _checkLinkedinAlmaMater(self, school, founderPage):
		#first, get linked in from founder page, if there is one
		linkedInUrl = self._getLinkedInUrl(founderPage)

		if linkedInUrl==None:
			return False
		else:
			#then founder has a linked in page
			#scrape for education, see if desired school is part of it
			try:
				response = urllib2.urlopen(linkedInUrl)
				page_source = response.read()
			except:
				#probably an invalid url
				return False


			lines = page_source.split('\n')

			schools = ''
			start = None
			end = None
			lineCount = 0
			for line in lines:
				if 'overview-summary-education-title' in line:
					start = lineCount
					
				if start:
					if '</dd>' in line:
						end = lineCount
						break

				lineCount += 1
			if not start==None and not end==None:
				educationBlock = ' '.join(lines[start:end])
				educations = re.findall(r'<a href=\".*?>(.*?)</a>',educationBlock)
					
				#check if alumni, for each education person has on linked in
				for education in educations:
					if self._isAlumni(education,school):
						return True
				return False

			else:
				#education section didn't exist on linkedin page
				return False

	def _getIsAlumniFromPage(self, school, foundersAndPages):
		print 'checking if each founder graduated from %s...' % (school)
		pbar = ProgressBar(maxval=len(foundersAndPages))
		pbar.start()
		count = 0

		founderIsAlumni = {}
		for founder in foundersAndPages:
			founderPage = foundersAndPages[founder]
			#check if college tag matches
			isAlmaMaterAngellist = self._checkCollegeTag(school, founderPage)
			
			if isAlmaMaterAngellist==None:
				#check linkedin
				isAlmaMaterLinkedin = self._checkLinkedinAlmaMater(school, founderPage)

				founderIsAlumni[founder] = isAlmaMaterLinkedin
			else:
				founderIsAlumni[founder] = isAlmaMaterAngellist

			count+=1
			pbar.update(count)

		pbar.finish()
		
		return founderIsAlumni

	def findFounderAlumni(self, city='NYC', school='Penn', topPct = 0.10, followMin = None):
		#get all startups in city
		startupUrls, startupNames = self._findStartups(city, topPct, followMin)

		#get founders of each startup
		foundersAndPages, foundersAndStartups = self._getFounders(startupUrls, startupNames)

		#for each founder, find out if belong to input school: first angellist tag, then linkedin
		isAlumni = self._getIsAlumniFromPage(school, foundersAndPages)

		resultDict = {}
		for founder in isAlumni:
			newrow = {}
			newrow['startup'] = foundersAndStartups[founder]
			newrow['isAlumni'] = isAlumni[founder]
			resultDict[founder] = newrow

		resultDf = DataFrame(resultDict).T

		return resultDf

		
	
