import requests
import ipdb as ipdb
import re
import angelist

#######################################################################################
# Scrapes Angelist for Upenn alumni.							                      #
#                                                                                     #
# Author: Troy Shu                                                                    #
# Email : tmshu1@gmail.com                                                            #
# Web: http://www.troyshu.com                                                         #
#                                                                                     #
#######################################################################################


class AngelistQuakerBot:
	def __init__(self):
		self.al = al.Angelist()
		self.al.client_id = '26e187d0f391e6fd2eb5cbef4f99d7a8'
		auth_url = self.al.getAuthorizationURL()

		ipdb.set_trace()
		
		self.al.client_secret = 'd2e0eb800bc28c638a987b8ed1cf64d0'


		
	
