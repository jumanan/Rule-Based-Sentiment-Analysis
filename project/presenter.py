from BeautifulSoup import BeautifulSoup, Tag
import os
import shutil

header="<HTML><HEAD></HEAD><style type='text/css'>td {font-size:75%;}</style><BODY>"
footer="</BODY></HTML>"
companyName = dict({})
FULLtickerList = ['MRK', 'C', 'DIS', 'NOK', 'GS', 'POT', 'KMB', 'LVS', 'INTC', 'AA']
tickerList = ['C', 'DIS', 'GS', 'INTC', 'AA']

def setup(path):
	if(os.path.exists(path + "present/")):
		shutil.rmtree(path + "present")
	os.mkdir(path + "present")
	os.mkdir(path + "present/data/")

def convertArticlesToHTML(path, ticker):
	pathToTicker = path + "present/data/"+ ticker + "/"
	os.mkdir(pathToTicker)
	allfiles = os.listdir(path + "articles/" + ticker + "_articles/")
	#filter file list - keep *_tagged.txt only
	taggedFiles = []
	for file in allfiles:
		if file.find("_tagged.txt") != -1:
			taggedFiles.append(file)
	
	for file in taggedFiles:
		nfile = file.partition(".")[0]
		openHTMLFile = open(pathToTicker + nfile + ".html", 'w')
		openHTMLFile.write("<HTML><HEAD></HEAD><BODY>")
		openFile = open(path + "articles/" + ticker + "_articles/"+ file,'r')
		lines = openFile.readlines()
		for line in lines:
			openHTMLFile.write(line)
			openHTMLFile.write("</br>\n")
		openHTMLFile.write(footer)
		openHTMLFile.close()
		openFile.close()
	
def presentCompany(path, ticker):
	articlesPath = path + "articles/"
	openHTMLFile = open(path +"present/data/"+ ticker + ".html", 'w')
	print path + "present/data/"+ ticker + ".html"
	openScoresFile = open(articlesPath + ticker +"_scores.txt", 'r')
	lines = openScoresFile.readlines()
	openHTMLFile.write(header)
	openHTMLFile.write("<h1><center>Ticker: " + ticker + " Company Name: " + companyName[ticker] + "</center></h1>")
	openHTMLFile.write("<table id='cssTable'>")
	openHTMLFile.write("<tr>")
	openHTMLFile.write("<td>VNEG</td>")
	openHTMLFile.write("<td>NEG</td>")
	openHTMLFile.write("<td>POS</td>")
	openHTMLFile.write("<td>VPOS</td>")
	openHTMLFile.write("<td>Tagged Article</td>")
	openHTMLFile.write("<td>Article</td>")
	openHTMLFile.write("<td>Date</td>")
	openHTMLFile.write("</tr>")
	vneg = 0
	neg = 0
	pos = 0
	vpos = 0
	for line in lines:
		openHTMLFile.write("<tr>")
		lineArray = line.split("\t")
		i=0
		for la in lineArray:
			if (i==0):
				la = la.partition(":")[2]
				vneg = vneg + int(la)
				openHTMLFile.write("<td>" + la + "</td>")
			if (i==1):
				la = la.partition(":")[2]
				neg = neg + int(la)
				openHTMLFile.write("<td>" + la + "</td>")
			if (i==2):
				la = la.partition(":")[2]
				pos = pos + int(la)
				openHTMLFile.write("<td>" + la + "</td>")
			if (i==3):
				la = la.partition(":")[2]
				vpos = vpos + int(la)
				openHTMLFile.write("<td>" + la + "</td>")
			if (i==4):
				openHTMLFile.write("<td><a href=" + ticker + "/" + la + "_tagged.html>" + la + "</a></td>")
			if (i==5):
				link = la					
			if (i==6):
				title = la
				openHTMLFile.write("<td><a href=" + link + ">" + title + "</a></td>")
			if (i==7):
				openHTMLFile.write("<td>" + la + "</td>")
			i = i + 1
		openHTMLFile.write("</tr>")
	
	openHTMLFile.write("</table><div id='totalvneg'>totalvneg=" + str(vneg) + "</div>")
	openHTMLFile.write("<div id='totalneg'>totalneg=" + str(neg) + "</div>")
	openHTMLFile.write("<div id='totalpos'>totalpos=" + str(pos) + "</div>")
	openHTMLFile.write("<div id='totalvpos'>totalvpos=" + str(vpos) + "</div>")
	openHTMLFile.write(footer)
	
	openHTMLFile.close()
	openScoresFile.close()

def readCompanyNames(path, file):
	openFile = open(path + file, 'r')
	lines = openFile.readlines()
	for line in lines:
		line = line.partition(":")
		companyName[line[0]]=line[2]
		
def calcScore(vneg,neg,pos,vpos):
	PplusN = int(vneg)*-2 +int(neg)*-1 + int(pos) + int(vpos)*2
	pMinusN = float(vneg)*2 + float(neg) + float(pos) + float(vpos)
	return str(PplusN/pMinusN)
	
def presentAllCompanies(path):
	tickerDataPath = path + "present/data/"
	openHTMLFile = open(path + "present/" + "index.html", 'w')
	openHTMLFile.write(header)
	openHTMLFile.write("<h1><center>COMPANY INDEX</center></h1>")
	openHTMLFile.write("<table id='cssCITable' align='center'>")
	openHTMLFile.write("<tr>")
	openHTMLFile.write("<td>VNEG</td>")
	openHTMLFile.write("<td>NEG</td>")
	openHTMLFile.write("<td>POS</td>")
	openHTMLFile.write("<td>VPOS</td>")
	openHTMLFile.write("<td>Score</td>")
	openHTMLFile.write("<td>Ticker</td>")
	openHTMLFile.write("<td>Company</td>")
	openHTMLFile.write("</tr>")
	
	contents = os.listdir(tickerDataPath)
	files = []
	for entry in contents:
		if (not(entry.partition(".")[2]=="")):
			files.append(entry)
	for file in files:
		openHTMLFile.write("<tr>")
		openFile = open(tickerDataPath + file,'r')
		s = BeautifulSoup(openFile)
		vneg = s.find("div",attrs={"id":"totalvneg"}).string.partition("=")[2]
		neg = s.find("div",attrs={"id":"totalneg"}).string.partition("=")[2]
		pos = s.find("div",attrs={"id":"totalpos"}).string.partition("=")[2]
		vpos = s.find("div",attrs={"id":"totalvpos"}).string.partition("=")[2]
		openHTMLFile.write("<td>" + vneg + "</td>")
		openHTMLFile.write("<td>" + neg + "</td>")
		openHTMLFile.write("<td>" + pos + "</td>")
		openHTMLFile.write("<td>" + vpos + "</td>")
		openHTMLFile.write("<td>" + calcScore(vneg,neg,pos,vpos) + "</td>")
		ticker = file.partition(".")[0]
		
		openHTMLFile.write("<td><a href=data/" + file.rpartition("/")[2] +">" + ticker + "</a></td>")
		openHTMLFile.write("<td>" + companyName[ticker] + "</td>")
		openHTMLFile.write("</tr>")
		openFile.close()
	openHTMLFile.write("</table>")
	openHTMLFile.write(footer)
	openHTMLFile.close()
	
	
readCompanyNames("project/tickers/", "companyList.txt")
print "initializing..."
setup("project/")
print "Converting articles to HTML.."
for ticker in tickerList:
	convertArticlesToHTML("project/",ticker)
	print "Creating page for " + ticker + "..."
	presentCompany("project/",ticker)
	print "done\n"
print "Creating main index page.."	
presentAllCompanies("project/")
print "all done\n"
print "open: project/present/index.html file to see the results."
