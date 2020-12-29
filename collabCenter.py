import requests
import json
import re
import time
from ftplib import FTP

def getListing(mlsNum):
	print ("getting mlsNum: " + mlsNum)
	x = requests.get("https://www.rew.ca/properties/search/build?utf8=%E2%9C%93&listing_search%5Binitial_search_method%5D=single_field&autocomplete%5Btype%5D=mls_num&autocomplete%5Bid%5D=&autocomplete%5Bvalue%5D={0}&listing_search%5Bquery%5D={0}".format(mlsNum))
	urlPath = "https://www.rew.ca" + json.loads(x.content)["path"]
	
	x = requests.get(urlPath)
	hasVirtualTour = False
	pictures = []
	for row in x.iter_lines():
		rowDecoded = row.decode("utf-8")

		if "<meta content=\"https://assets-listings.rew.ca/brc_idx_rew/brc/" in rowDecoded:
			imgSrc = re.search("content=\"(.*?)\"", rowDecoded).group(1)
			pictures.append(imgSrc)
		elif "id=\"virtualTour\"" in rowDecoded:
			hasVirtualTour = True

	return {
		"mlsNum": mlsNum,
		"pictures": pictures,
		"urlPath": urlPath,
		"hasVirtualTour": hasVirtualTour
	}

retArray = []
def getListings(mlsNums):
	for mlsNum in mlsNums:
		retArray.append(getListing(mlsNum))
		time.sleep(5) # rew.ca doesn't load data if you hit it too much

	print(retArray)
	return retArray

if __name__ == '__main__':

	# create data.js info dump
	mlsNums = []
	with open('jsonRequest.txt', 'r') as file, open('data.js', 'w') as jsFile:
		collabData = json.load(file)
		mlsNums = (o["DISPLAY_ID"] for o in collabData["ListingInfo"])

		resp = getListings(mlsNums)

		jsonStr = json.dumps(resp)
		jsonStr2 = json.dumps(collabData)
		jsFile.write("var globalData = { \"rewData\": "+jsonStr+", \"collabData\": "+jsonStr2+" }")

	# upload it to ftp server
	with open('ftpCredentials.txt', 'r') as file:
		creds = json.load(file)

		ftp = FTP(creds["host"], creds["usr"], creds["pwd"])
		ftp.cwd('public_html/2020CollabCenter')
		ftp.retrlines('LIST')
		with open('data.js', 'rb') as dataFile:
			ftp.storbinary('STOR data.js', dataFile)
		ftp.quit()


	print("... done")
