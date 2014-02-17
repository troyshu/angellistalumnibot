import requests
import oauth2 as oauth
import urlparse
import ipdb as ipdb
import re
import angellist
reload(angellist)
from werkzeug.urls import *

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


	def _findStartups(self, city='NYC', topPct = 0.10, followMin = None):
		print 'getting all startups in %s:' % city

		getLocationId = self.locationTagIdMap[city]

		#get all startups in city
		startupIds = []
		pageCount = 1
		count = 0
		perPage = 50
		while True:
			print 'getting page %s of startups...' % (pageCount)

			#get most popular startups first
			search_response = self.al.getTagsStartups(self.al.access_token, getLocationId, order='popularity', per_page = perPage, page=pageCount)

			#extract all startup ids
			startups = search_response['startups']

			for startup in startups:
				startupIds.append(startup['id'])

				#if we've reached a min follower count, break
				if followMin and int(startup['follower_count'])<followMin:
					break


			count += perPage
			#if we reached the end
			if count > int(search_response['total']):
				break
			#if we reached more than topPct of most popular startups (by followers)
			if count > topPct*float(search_response['total']):
				break
			#if we've reached a min follower count, break
			if followMin and int(startup['follower_count'])<followMin:
				break

			pageCount += 1

			ipdb.set_trace()





		
	
