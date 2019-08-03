from BeautifulSoup import BeautifulSoup
import urllib2
import re
import os
import sys
import shutil
import datetime

tickers = ["MRK"]#, "C", "DIS", "NOK", "GS", "POT", "KMB", "LVS", "INTC", "AA"]

stockMarket = 'NYSE'
startDate = '2010-03-09'
endDate = '2010-04-09'
startArticle = '0'
endArticle = '2000'


def cleanUp():
	yahooPath = 'project/tickers/yahoo'
	googlePath = 'project/tickers/google'
	print("cleaning up...")
	if(os.path.exists(yahooPath)):
		print("deleting " + yahooPath)
		shutil.rmtree(yahooPath)
	if(os.path.exists(googlePath)):
		print("deleting " + googlePath)
		shutil.rmtree(googlePath)
	os.mkdir(yahooPath)
	os.mkdir(googlePath)
	print(" done.\n")
		
def googleCrawler():
	print("Downloading articles from Google Finance:\n")
	for ticker in tickers:
		
		filePath = 'project/tickers/google/tickers-' + ticker + '.txt'
		if(os.path.exists(filePath)):
			os.remove(filePath)
        
		openfile = open(filePath, 'w')
		if(ticker == "INTC"):
			stockMarket = 'NASDAQ'
		else:
			stockMarket = 'NYSE'
		searchStr = 'http://www.google.com/finance/company_news?q=' + stockMarket+':' + ticker + '&startdate=' + startDate + '&enddate=' + endDate + '&start=' + startArticle + '&num=' + endArticle
		page = urllib2.urlopen(searchStr) #opens the page
		s = BeautifulSoup(page) # creates the soup
		linksParags = s.findAll('div',attrs={"class":"g-section news sfe-break-bottom-16"})
		#links = s.findAll('a',attrs={"id":"n-cn-"})
		#dates = s.findAll('span', attrs={"class":"date"})
		
		for para in linksParags:
			link = para.find('a', attrs={"id":"n-cn-"})["href"]
			date = para.find("span", attrs={"class":"date"})
			openfile.write(link.encode('utf8') + "\t" + date.string.encode('utf8') + "\n")
		openfile.close()
		print('ticker ' + ticker + ' done. Links downloaded: ' + str(len(linksParags)) +'\n')
	print("all done")

def yahooCrawler():
	print("Downloading articles from Yahoo Finance:\n")
	
	for ticker in tickers:
		total = 0
		day = 28
		restOfDate = '2010-02-'
		filePath = 'project/tickers/yahoo/tickers-' + ticker + '.txt'
		if (os.path.exists(filePath)):
			os.remove(filePath)
			
		openfile = open(filePath, 'w')
		z = range(5)
		for num in z:
			day = day - 7*num
			searchStr = 'http://finance.yahoo.com/q/h?s=' + ticker + '&t=' + restOfDate + str(day)
			page = urllib2.urlopen(searchStr)
			s = BeautifulSoup(page)
			s = s.find('table', attrs={"class":"yfncnhl"})
			links = s.findAll('a')
			total = total + len(links)
			for a in links:
				linkResult = a["href"].partition("*")
				if (linkResult[2]==""):
					linkResult = linkResult[0]
				else:
					linkResult = linkResult[2]
				linkResult = linkResult.replace("%3A",":")
				openfile.write(linkResult+"\n")
		openfile.close()
		print('ticker ' + ticker + ' done. Links downloaded: ' + str(total) +'\n')
	print("all done")

def calcStartAndEndDate():
	now = datetime.datetime.now()
	endDate = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
	startDate = str(now.year) + "-" + str(now.month - 1) + "-" + str(now.day)
	
calcStartAndEndDate()
tickers=eval(sys.argv[2])
openFile = open("project/tickers/tickersList.txt",'w')
for ticker in tickers:
	openFile.write(ticker + "\n")
openFile.close()

cleanUp()
if (sys.argv[1]=="Google"):
	googleCrawler()
else:
	if (sys.argv[1]=="Yahoo"):
		yahooCrawler()
	else:
		if (sys.argv[1]=="MSN"):
			msnCrawler()
		else:
			if (sys.argv[1]=="StreetInsider"):
				ssCrawler()
			else:
				print("Wrong usage - must provide site name: Google, Yahoo, MSN, or StreetInsider")
