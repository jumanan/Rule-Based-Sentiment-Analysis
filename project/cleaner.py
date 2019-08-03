from BeautifulSoup import BeautifulSoup, Comment, Tag, NavigableString
import urllib2
import re
import httplib
import os
import sys
import shutil
import nltk

#coding=utf-8 
articlesPath = 'project/articles/'
tickersPath = 'project/tickers/'


def getPlace(tag):
	place = 0
	while (not(tag.previousSibling == None)):
		tag = tag.previousSibling
		place = place + 1
	#print ("son place = ", place)
	return place
	
def simplifySoup(s):

	formatting = ['strong', 'em', 'b', 'i']
	#remove all strong, em , b tags
	for form in formatting:
		#print ("deleting ======> " + form)
		try:
			tags = s.findAll(form)
		except AttributeError, e:
			print "article download failed"
			return s
		for tag in tags:
			#print("FOR STRONG TAG:")
			place = getPlace(tag)
			size = len(tag.contents)
			#print("size = ", size)
			i = 0
			#print("BEFORE : ")
			#print(tag.parent)
			for son in tag:
				#print("moving = "+ str(son))
				tag.parent.insert(place+i, son.extract())
				i = i + 1
			#print("AFTER : ")
			parent = tag.parent
			tag.extract()
			#print(parent)
	
	#if span/div inside p - remove span/div
	paras = s.findAll('p')
	for p in paras:
		#print("FOR SPAN TAG IN P:")
		tags = p.findAll('span')
		for tag in tags:
			#print("FOR SPAN TAG:")
			place = getPlace(tag)
			size = len(tag.contents)
			#print("size = ", size)
			i = 0
			#print("BEFORE : ")
			#print(tag.parent)
			for son in tag:
				#print("moving = "+ str(son))
				tag.parent.insert(place+i, son.extract())
				i = i + 1
			#print("AFTER : ")
			parent = tag.parent
			tag.extract()
			#print(parent)
		
			
	paras = s.findAll('p')
	for p in paras:
		tags = p.findAll('div')
		for tag in tags:
			#print("FOR DIV TAG IN P:")
			place = getPlace(tag)
			size = len(tag.contents)
			#print("size = ", size)
			i = 0
			#print("BEFORE : ")
			#print(tag.parent)
			for son in tag:
				#print("moving = "+ str(son))
				tag.parent.insert(place+i, son.extract())
				i = i + 1
			#print("AFTER : ")
			parent = tag.parent
			tag.extract()
			#print(parent)
		
	
	#removing font and span inside a td
	tds = s.findAll('td')
	for td in tds:
		tags = td.findAll('font')
		for tag in tags:
			#print("FOR FONT TAG IN TD:")
			place = getPlace(tag)
			size = len(tag.contents)
			#print("size = ", size)
			i = 0
			#print("BEFORE : ")
			#print(tag.parent)
			for son in tag:
				#print("moving = "+ str(son))
				tag.parent.insert(place+i, son.extract())
				i = i + 1
			#print("AFTER : ")
			parent = tag.parent
			tag.extract()
			#print(parent)
		
			
	tds = s.findAll('td')
	for td in tds:
		tags = td.findAll('span')
		for tag in tags:
			#print("FOR SPAN TAG IN TD:")
			place = getPlace(tag)
			size = len(tag.contents)
			#print("size = ", size)
			i = 0
			#print("BEFORE : ")
			#print(tag.parent)
			for son in tag:
				#print("moving = "+ str(son))
				tag.parent.insert(place+i, son.extract())
				i = i + 1
			#print("AFTER : ")
			parent = tag.parent
			tag.extract()
			#print(parent)
	return s
		

def getCompanyNames(path, fileName):
	openFile = open(path + fileName, 'r')
	tickers = openFile.readlines()
	newFile = open(path + "companyList.txt", 'w')
	print("Detecting company names for given tickers..\n")
	for ticker in tickers:
		print("Ticker: " + ticker)
		page = None
		try:
			page = urllib2.urlopen("http://moneycentral.msn.com/companyreport?symbol=" + ticker)
		except urllib2.HTTPError, e:
			print "HTTP ERROR EXCEPTION"
			continue
		except urllib2.URLError, e:
			print "URL ERROR EXCEPTION"
			continue
		except error, e:
			print "EXCEPTION"
			continue
		if (page==None):
			print("error opening: " + "http://moneycentral.msn.com/companyreport?symbol=" + ticker)
		else:
			s = BeautifulSoup(page)
			s = s.find('h1', attrs={"class":"h1a"})
			s = s.text
			companyName = s.partition(":")[0]
			print("Company Name: " + companyName +'\n')
			ticker = ticker.partition("\n")[0]
			newFile.write(ticker + ":" + companyName + "\n")
	openFile.close()
	newFile.close()
			
def createCompanyMap(path, fileName):
	openFile = open(path + fileName, 'r')
	lines = openFile.readlines()
	openFile.close()
	companyMap = dict({})
	for line in lines:
		partition = line.partition(":")
		companyMap[partition[0]] = partition[2]
	return companyMap

def deleteDirectories():
	if(os.path.exists(articlesPath)):
		#print("deleting " + articlesPath)
		shutil.rmtree(articlesPath)
	os.mkdir(articlesPath)

def removeMenus(sp):

	# remove menus/link tables
	try:
		tables = sp.findAll('ul')
	except AttributeError, e:
		print "article download failed"
		return sp
	for table in tables:
		if (table.fetch('a') > 4):
			table.extract()
			
	#remove footers
	tags=sp.findAll('div', attrs={'id':re.compile('(footer.*)|(.*footer)')})
	for tag in tags:
		#print("deleting====================" + str(tag))
		tag.extract()
		
	#remove comments section
	tags=sp.findAll('div', attrs={'id':re.compile('(comment.*)|(.*comment)')})
	for tag in tags:
		#print("deleting====================" + str(tag))
		tag.extract()
	
	#remove tr/td with direct #'a'>4 as childrens
	tags = sp.findAll('tr')
	for tag in tags:
		if (len(tag.findAll('a', recursive=False))>3):
			tag.extract()
	tags = sp.findAll('td')
	for tag in tags:
		if (len(tag.findAll('a', recursive=False))>3):
			tag.extract()
		
	#remove tags that doesn't contain enough text (len<20)
	tags = sp.findAll(text=lambda text:isinstance(text, NavigableString))
	for tag in tags:
		if(len(tag)<20):
			#print("REMOVED= " + tag + '\n')
			tag.extract()
	return sp	
					        
#deletes garbage before html and after html tags, deleted comment tags
def cleanSoup(sp1):
	if (sp1==None):
		return sp1
	else:
		#remove all garbage before and after HTML tag
		sp1 = sp1.html
		#remove <SCRIPT>
		try:
			to_extract = sp1.findAll('script')
		except AttributeError, e:
			return sp1
		for item in to_extract:
			item.extract()
		
		#remove <style>
		to_extract = sp1.findAll('style')
		for item in to_extract:
			item.extract()
		#remove <!-- comments
		comments = sp1.findAll(text=lambda text:isinstance(text, Comment))
		[comment.extract() for comment in comments]
		return sp1
	
	
def getTicker(fileName):
	ticker = fileName.partition("-")[2]
	ticker = ticker.partition(".")[0]
	return ticker;
	
def downloadAndCleanAll(siteName, companyMap):
	tickersFiles = os.listdir(tickersPath + siteName)
	if (not(os.path.exists(articlesPath))):
		os.mkdir(articlesPath)
	for fileName in tickersFiles:    
		ticker = getTicker(fileName)
		print("reading file: " + fileName + " of ticker: " + ticker)
		if (not(os.path.exists(articlesPath + ticker + '_articles/'))):
			os.mkdir(articlesPath + ticker + '_articles')
		readfile= open(tickersPath + siteName + '/tickers-'+ ticker + '.txt','r')
		links=readfile.readlines()
		
		openLogFile = open(articlesPath + ticker + '_logFile' + '.txt', 'w')
		i = 0
		for linkWithDate in links:
			i = i + 1
			link = linkWithDate.partition("\t")[0]
			date = linkWithDate.partition("\t")[2]
			print('opening: ' + link)
			try:
				page = urllib2.urlopen(link).read()
			except urllib2.HTTPError, e:
				print "HTTP ERROR EXCEPTION"
				continue
			except urllib2.URLError, e:
				print "URL ERROR EXCEPTION"
				continue
			except Exception, e:
				print "OTHER ERROR"
				continue
			
			s = BeautifulSoup(page)
			articleName = 'article' + str(i);
			openTextFile = open(articlesPath + ticker + '_articles/' + articleName + '.txt', 'w')
			openHTMLFile = open(articlesPath + ticker + '_articles/' + articleName + '.html', 'w')
			try:
				openLogFile.write(articleName + "\t" + link.rstrip('\n') + "\t" + s.title.string.strip().strip('\n').replace('\n','') +"\t" + date.strip("\n") +  "\n")
			except UnicodeEncodeError, e:
				print "error writing to file"
				continue
			except AttributeError, e:
				print "error writing to file"
				continue
			
			if (s==None):
				print "Failed to download article"
				continue
			# clean process (scripts, comments)
			print("cleaning article..")
			s = cleanSoup(s)
			print("simplifying article..")
			s = simplifySoup(s)
			print("removing menus, ads, and links...")
			s = removeMenus(s)			
			try:
				s.findAll("div")
			except AttributeError, e:
				continue
			#resFile = s2.findAll('p','div',text=lambda(x): len(x.split(' ')) > 20)
			companyName = companyMap[ticker].partition(" ")[0]
			#resFile = s.findAll(text=lambda(x): ((len(x.split(' ')) > 20) or (x.find(ticker)!=-1) or (x.find(companyName)!=-1)))

			openHTMLFile.write(s.prettify())
			openHTMLFile.close()
			
			results = s.findAll(text=True)
			for res in results:
				#.replace("&amp;","&").replace("&nbsp;"," ").replace("&acute;","'")
				openTextFile.write(re.sub("\s\s\s*"," ",res.encode('utf8').replace("&amp;","&").replace("&nbsp;"," ").replace("&acute;","'")) + "\n")
			openTextFile.close()
			
			print("end reading\n\n");
		openLogFile.close()
	print("\ndone reading");

#========================

#getCompanyNames("project/tickers/","tickersList.txt")
deleteDirectories()
theMap = createCompanyMap("project/tickers/","companyList.txt")
downloadAndCleanAll(sys.argv[1], theMap)
