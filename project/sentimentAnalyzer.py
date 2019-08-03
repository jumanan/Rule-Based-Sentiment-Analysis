import  nltk, re, pprint, sys, os
from nltk.parse import load_earley
from nltk.sem import drt
import os


posWordsMap = dict({})
negWordsMap = dict({})
intensifyWordsMap = dict({})
porter = nltk.PorterStemmer()


def loadDictionary(path, fileName, score,stem):
	wordsMap = dict({})
	openFile = open(path + fileName,'r')
	lines = openFile.readlines()
	for line in lines:
		if stem =='true':
			wordsMap[porter.stem(line.partition("\n")[0])] = score
		else:
			wordsMap[line.partition("\n")[0]] = score
	openFile.close()
	return wordsMap

#add value to an already created dictionary
def addValuesToDic(wordsMap, path, fileName, score,stem):
	openFile = open(path + fileName,'r')
	lines = openFile.readlines()
	for line in lines:
		if stem =='true':
			wordsMap[porter.stem(line.partition("\n")[0])] = score
		else:
			wordsMap[line.partition("\n")[0]] = score
	openFile.close()
	return wordsMap

#write dictionaries to a file
def dumpAll():
	openFile = open('project/dictionary/all.txt','w')
	for key in posWordsMap:
		openFile.write(key + " " + str(posWordsMap[key]) + "\n")
	for key in negWordsMap:
		openFile.write(key + " " + str(negWordsMap[key]) + "\n")
	for key in intensifyWordsMap:
		openFile.write(key + " " + str(intensifyWordsMap[key]) + "\n")
	openFile.close()
	
#tag the phrase inside tagValue with color tagging according to value
def tagText(tagValue,sentence,value):
	color = ['firebrick','red','','green','lime'][value + 2]
	if re.search("\t",sentence) !=None:
		return sentence.replace(tagValue, "<b><font color='" + color + "'>" + tagValue + "</font></b>")
	textPattern = ""
	for word in tagValue.split(" "):
		textPattern = textPattern + "(\s*\t*\s*)" + word
		textPattern = textPattern.replace("|"," ")
	return re.sub(textPattern, "<b><font color='" + color + "'>" + tagValue + "</font></b>",sentence); 

#remove POS taggings and return a string
def getTagValue(tree):
	taggedString = "";
	for elem in tree:
		taggedString = taggedString + " " + elem[0]
	return taggedString

#make sure the score is between [-2,2]
def normalizeScore(score):
	if score>0:
		return min(score,2)
	return max(-2,score)

#evaluate verbs
def evalVerbs(subtree,preValue):
	# positive verbs get the value of their object or their value if they have none
	
	#events
	value = eventWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
	if (value != None):
		if ((subtree[0])[0].upper() in ['RELEASES','RELEASED','RELEASING','RELEASE'] and str(subtree).find("new")==-1):
			return 0;
		return value;
	
	#special case avoid switches polarity
	if (subtree[0])[0].upper() in ['AVOID','AVOIDS','AVOIDING','AVOIDED','PREVENT', 'PREVENTS','PREVENTING','PREVENTED']:
		del subtree[0];
		return -1 * evalExpr(subtree,preValue);
	
	#positive verbs
	value = posWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
	if (value != None and not (((subtree[0])[0]).upper() in ['LEAD','LED','LEADS','LEADING'])):
		del subtree[0];
		new_value = evalExpr(subtree,preValue);
		if (new_value !=0):
			return new_value
		else:
			return value;
	else:
		# negative verbs reverse the value of their object
		value = negWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
		verb = porter.stem((subtree[0])[0].upper())
		if (value != None):
			if ("PAY" == (porter.stem((subtree[0])[0].upper())) and 
			"ATTENTION" == ((subtree[1])[0]).upper() ):
				del subtree[0]
			else:
				del subtree[0];
				new_value = evalExpr(subtree,preValue);
				if (new_value !=0):
					if (verb == "FELL"):
						return new_value
					return -1 * new_value
				else:
					return value;

		#neutral verb
		del subtree[0];
		return evalExpr(subtree,preValue);

#evaluate not
def evalNot(subtree,preValue):
	del (subtree[0])
	if (subtree.height()> 2 and (subtree[0])[0].lower() in ['only']):
		del(subtree[0])
		return 2 * evalExpr(subtree,preValue);
	return -1 * evalExpr(subtree,preValue);
	
#evaluate nouns
def evalNouns(subtree,preValue):
	if (subtree[0])[0].upper() in ['HAZARDOUS'] and subtree.height()> 1 and (subtree[1])[0].upper() in ['WASTE']:
		del subtree[0]
		return 0;
	#events
	value = eventWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
	if (value != None):
		if ((subtree[0])[0].upper() in ['RELEASES','RELEASED','RELEASING','RELEASE'] and str(subtree).find("new")==-1):
			return 0;
		return value;
	
	value = posWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
	if (value != None and not ((subtree.height()> 2 and (subtree[1])[0].lower() in ['up','down','towards', 'to']))):
		return value
		
	else:
		value = negWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
		if (value != None):
			return value;
		else:
			#neutral noun => evaluate the rest of the expression
			del (subtree[0]);
			return evalExpr(subtree,preValue);

#evaluate adjectives
def evalAdj(subtree,preValue):
	value = posWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
	if (value == None):
		value = negWordsMap.get(porter.stem((subtree[0])[0].upper()),None);
		if (value ==None): #neutral
			del (subtree[0]);
			return evalExpr(subtree,preValue);
	del (subtree[0]);
	
	if (subtree.height() != 1 and re.match("N.*", (subtree[0])[1]) != None):
		nounVal = evalNouns(subtree,preValue + value);
		if (nounVal != 0):
			if (value + preValue == 0 or nounVal < 0):
				newValue = nounVal;
			else:
				newValue = nounVal * (value + preValue);
		else: #neutral noun
			newValue = value + preValue;
		return normalizeScore(newValue);
	#next word is not a noun
	nextValue = evalExpr(subtree,preValue + value)
	return nextValue;
	
	

#evaluate expression
def evalExpr(subtree,preValue):
	ignore = True
	value = 0;
	while (ignore and subtree.height() != 1):
		
		#check if it's one of the intensify words
		intensifyValue = intensifyWordsMap.get((subtree[0])[0].upper(),None);
		if (intensifyValue != None):
			intensityWord = (subtree[0])[0].upper()
			del (subtree[0])
			new_val = evalExpr(subtree,preValue)
			if (new_val != 0):
				return intensifyValue * new_val
			#intensify word on its own
			if (intensityWord in ['BEST','HIGHEST','LOWEST','LOWER','UNDISPUTED',
					'UNEQUIVOCAL','UNPARALLELED','UNSURPASSED']):
					return value;
		#evaluate verb
		if (subtree.height() != 1 and (subtree[0])[1].find('VB') != -1):
			return evalVerbs(subtree,preValue);
		else:#NP expression
			if (subtree.height() != 1 and re.match("N.*", (subtree[0])[1]) != None):

				return evalNouns(subtree,preValue);
			else:#"not NP/VP" expression
				if (subtree.height() != 1 and (subtree[0])[1].find('RB') != -1):
					if ((subtree[0])[0].find('not') != -1  or (subtree[0])[0].find('never') != -1):
						
						return evalNot(subtree,preValue);
					else:
						if (subtree.height() != 1 and re.match('(u|U)(p|P)',str(subtree[0])[0])) != None:
						
							return 1;
						if (subtree.height() != 1 and re.match("(down|Down|DOWN)",(subtree[0])[0])!= None):
						
							return -1;
						#adverb
						
						return evalAdj(subtree,preValue);
				else:#"no NP" expresssion
					if (subtree.height() != 1 and (subtree[0])[1].find('DT') != -1 and (subtree[0])[0].find('no') != -1 ):
						
						return evalNot(subtree,preValue);
					else:#adjectives
						if (subtree.height() != 1 and (subtree[0])[1].find('JJ')!=-1):
						
							return evalAdj(subtree,preValue);
						if (subtree.height() != 1 and re.match('(u|U)(p|P)',str(subtree[0])[0])) != None:
						
							return 1;
						if subtree.height() != 1 and ((subtree[0])[0]).find('above') != -1:
						
							return 1;
						if (subtree.height() != 1 and re.match("(down|Down|DOWN)",(subtree[0])[0])!= None):
						
							return -1;
						#skip tag
						del (subtree[0]);
										
	return preValue


#check if the expression is about the ticker
def isAboutTicker(ERTaggedSentence,expression,companyName):
	entity = ""
	taggedSentence = (re.sub("\s\s+"," ",ERTaggedSentence).replace("\n", " "))
	endIndex = taggedSentence.rfind(expression.split()[0])
	startIndex = taggedSentence.rfind("(",0,endIndex)
	while taggedSentence[startIndex] != " ":
		startIndex = startIndex + 1;
	while taggedSentence[startIndex] != ")":
		entity = entity + taggedSentence[startIndex];
		startIndex = startIndex + 1;
	if (entity!=""):
		return re.search("(?![A-Z])" + companyName[0] + "(?![A-Z])",expression) != None or expression.find(companyName[1])!=-1 or re.search("(?![A-Z])" + companyName[0] + "(?![A-Z])",entity) != None or entity.find(companyName[1])!=-1 or taggedSentence.find(companyName[0],startIndex,endIndex)!=-1 or taggedSentence.find(companyName[1],startIndex,endIndex)!=-1

			
#evaluate article return [vneg,neg,pos,vpos] recieves file  + company and ticker name 
def evalArticle(fileName,companyName):

	readfile= open(os.path.join(companyDir,fileName),'r')
	output = open(os.path.join(companyDir,fileName.replace(".txt" , "_tagged.txt")),'w')
	screenDump = open(os.path.join(companyDir,fileName.replace(".txt" , "_dump.txt")),'w')
	
	lines=readfile.readlines()
	text = ""
	for line in lines:
		text = text + (re.sub("\s\s+"," ",(re.sub("\s*-\s*"," ",line)).replace("("," ").replace(")", " ")));
	readfile.close();
	
	# split sentences
	sentences = nltk.sent_tokenize(text)
	#tokanize sentences
	words = [nltk.word_tokenize(sent) for sent in sentences]
	#part of speach tagging (POS)
	taggedSentences = [nltk.pos_tag(word) for word in words]

	#named entity recognition	
	ERTagged = [nltk.ne_chunk(sentence) for sentence in taggedSentences]

	cp_verb_object = nltk.RegexpParser('VERB: {<JJR>?<V.*><CD>?(<RB>|<TO>)*<V.*>*(<IN>?(<PRP.*>|<DT>)?<RB>?<CD>?<JJ.*>*<N.*>?<N.*>?<N.*>?<JJ.*>*)*}')
	cp_nouns = nltk.RegexpParser('NOUN: {<DT>?<RB>*<N.*>?<N.*>?<N.*>?<CD>?(<JJ.*>+<CD>?<N.*>?<N.*>?<N.*>?<N.*>?)|(<JJ.*>*<CD>?<N.*><N.*>?<N.*>?<N.*>?)}')
	cp_up_down = nltk.RegexpParser('UPDOWN: {<RB><TO>?<CD>}')
	up = re.compile(r"\('(u|U)p'\s*,\s*'RB'\)")
	down = re.compile(r"\('(d|D)own'\s*,\s*'RB'\)")

	i = 0;
	total = 0;
	sntmnt = [0,0,0,0,0]
	for sentence in taggedSentences:
		screenDump.write("\n----------------------------------" +
		"\noriginal sentence: \n" + sentences[i] +
				"\n\n" + "POS tagged sentence: \n" + re.sub("\n"," " ,str(sentence)) +"\n" +
				"\n\n" + "ERTAGGED sentence: " + str(ERTagged[i]).replace("\n", " "))
		
		ERTagged_companySentence =str(ERTagged[i]);
		if (re.search(companyName[0] + "(?![A-Z])",sentences[i]) == None and sentences[i].find(companyName[1]) ==-1):
			#if the sentence contains the company, then see if it belongs to the ticker being checked if so
			#evaluate it
			ERTagged_companySentence = re.sub("\s\s+", " ",str(ERTagged[i]).replace("\n", " "))
			index = ERTagged_companySentence.lower().find("the/dt company/nn")
			if (index!=-1):
				j = i;
				lastOrganization_index = re.sub("\s\s+", " ",str(ERTagged[i]).replace("\n", " ")).rfind("(ORGANIZATION",0,index);
				lastPerson_index = re.sub("\s\s+", " ",str(ERTagged[i]).replace("\n", " ")).rfind("(PERSON",0,index);
				if (lastOrganization_index!=-1 or lastPerson_index !=-1):
					output.write(sentences[i]);
					i = i + 1
					continue;
				while(lastOrganization_index == -1 and lastPerson_index == -1 and j!=-1):
					j = j -1;
					ERTagged_sentence = re.sub("\s\s+", " ",str(ERTagged[j]).replace("\n", " "))
					lastOrganization_index = ERTagged_sentence.rfind("(ORGANIZATION");
					lastPerson_index = ERTagged_sentence.rfind("(PERSON");		
				if (lastOrganization_index != -1 or lastPerson_index != -1):
					if (lastOrganization_index >lastPerson_index):
						last_index = ERTagged_sentence.rfind(")");
						if (ERTagged_sentence.rfind(companyName[0],lastOrganization_index,last_index)!= -1 or ERTagged_sentence.rfind(companyName[1],lastOrganization_index,last_index)!= -1):
							ERTagged_companySentence = ERTagged_companySentence[:index] +  "(ORGANIZATION " + companyName[0] + "/NNP)"+ ERTagged_companySentence[index+17:]							
						else:
							output.write(sentences[i]);
							i = i + 1
							continue;
					else:
						last_index = ERTagged_sentence.rfind(")");
						if (ERTagged_sentence.rfind(companyName[0],lastPerson_index,last_index)!= -1 or ERTagged_sentence.rfind(companyName[1],lastPerson_index,last_index)!= -1):
							ERTagged_companySentence = ERTagged_companySentence[:index] +  "(ORGANIZATION " + companyName[0] + "/NNP)" + ERTagged_companySentence[index+17:]
						else:
							output.write(sentences[i]);
							i = i + 1
							continue;
			else:
				output.write(sentences[i]);
				i = i + 1
				continue;
		
		#extract phrases like up/down number and evaluate them
		tree = cp_up_down.parse(sentence)
		screenDump.write("Up/down number phrases to consider:\n")
		for subtree in tree.subtrees():
			if (subtree.node == 'UPDOWN'):
				if up.match(str(subtree[0])) != None:
					screenDump.write("\t" + re.sub("\n", " " ,str(subtree)) + "\n");
					tagValue = getTagValue(subtree);
					sentences[i] = tagText(tagValue,sentences[i],1)
					total = total + 1;
					sntmnt[3] = sntmnt[3] + 1
					screenDump.write("\ntagged sentence:\n" + "\t" + tagValue +"\tres:"+ "+1" + "\n");
				else:
					if down.match(str(subtree[0])) != None:
						screenDump.write("\t" + re.sub("\n", " " ,str(subtree)) +"\n");
						tagValue = getTagValue(subtree);
						sentences[i] = tagText(tagValue,sentences[i],-1)
						total = total + 1;
						sntmnt[1] = sntmnt[1] + 1
						screenDump.write("'\ntagged sentence:\n" + "\t" + tagValue + "\tres:"+ "-1" +"\n");
		# extract verbs & their objects & evaluate them
		tree = cp_verb_object.parse(tree)
		screenDump.write("verb phrases to consider:\n")
		for subtree in tree.subtrees():
			if subtree.node == 'VERB': 
				screenDump.write("\t" + re.sub("\n", " " ,str(subtree)) + "\n");
				tagValue = getTagValue(subtree);
				tmp = str(subtree).replace("VERB","").replace("(","").replace(")","").replace("\n", " ")
				res = evalExpr(subtree,0)
				if (res != 0):
					res = normalizeScore(res);
					if (isAboutTicker(ERTagged_companySentence,tmp,companyName)):
						sntmnt[2+res] = sntmnt[2+res] + 1
						sentences[i] = tagText(tagValue,sentences[i],res)
						screenDump.write("\ntagged sentence:\n" + "\t" + tagValue + "\tres:"+ str(res) + "\n");
			
		#extract noun phrases and evaluate them
		tree = cp_nouns.parse(tree)
		screenDump.write("noun phrases to consider:\n")
		for subtree in tree.subtrees():
			if subtree.node == 'NOUN': 
				screenDump.write("\t" + re.sub("\n", " " ,str(subtree)) + "\n");
				tagValue = getTagValue(subtree);
				tmp = str(subtree).replace("NOUN","").replace("(","").replace(")","").replace("\n", " ")
				res = evalExpr(subtree,0)
				if (res != 0):	
					res = normalizeScore(res);
					if (isAboutTicker(ERTagged_companySentence,tmp,companyName)):
						total = total + abs(res);
						sntmnt[2+res] = sntmnt[2+res] + 1
						sentences[i] = tagText(tagValue,sentences[i],res)
						screenDump.write("\ntagged sentence:\n" + "\t" + tagValue + "\tres:"+ str(res) +"\n");
		
		output.write(sentences[i]);
		i = i + 1
		
		
	screenDump.write("\n\n" + "veryneg:" + str(sntmnt[0]) + "\tneg:" + str(sntmnt[1]) + 
		"\tpos:" + str(sntmnt[3]) + "\tverypos:" + str(sntmnt[4]) + "\ttotal:" + str(total));
	output.close();
	screenDump.close()
	return sntmnt
	
basicDir = os.path.join(sys.path[0], '../');
articlesDir = os.path.join(basicDir,"project/articles");

print("loading dictionaries...\n")
posWordsMap = loadDictionary('project/dictionary/','positive.txt', +1,'true')
negWordsMap = loadDictionary('project/dictionary/','negative.txt', -1,'true')
intensifyWordsMap = loadDictionary('project/dictionary/','modalStrong.txt', +2,'false')
intensifyWordsMap['LOWEST'] = - 2
eventWordsMap = loadDictionary('project/dictionary/','good_events.txt', +2,'true')
addValuesToDic(eventWordsMap,'project/dictionary/','bad_events.txt', -2,'true')
print("dumping dictionaries...\n")
dumpAll()

tickers = []
companyNames = []
companyList = open(os.path.join(basicDir,"project/companyList.txt"),"r")
companies = companyList.readlines();
for line in companies:
	line = line.split(":")
	tickers.append(line[0].strip());
	companyNames.append([line[0].strip(),line[1].replace("Inc","").replace("& Co","").replace("Corp","").replace("Co","").strip()])

i = 0;
for ticker in tickers:
	print "working on ticker - ",ticker,"-",companyNames[i][1],"\n"
	companyDir = os.path.join(articlesDir,ticker + "_articles");
	tickerLog = open(os.path.join(articlesDir, ticker + "_logFile" + ".txt"),'r')
	tickerScores = open(os.path.join(articlesDir, ticker + "_scores" + ".txt"),'w')
	for articleInfo in tickerLog.readlines():
		file = articleInfo.split()[0] +".txt"
		if (re.match("article\d+.txt",file)!=None):
			score = evalArticle(file, companyNames[i]);
			print "\tArticle: ", file, 
			print (" results:\t" + "veryneg:" + str(score[0]) + "\tneg:" + str(score[1]) +
			"\tpos:" + str(score[3]) + "\tverypos:" + str(score[4]))
			tickerScores.write("veryneg:" + str(score[0]) + "\tneg:" + str(score[1]) + 
			"\tpos:" + str(score[3]) + "\tverypos:" + str(score[4]) + "\t" + articleInfo);
		else:
			tickerScores.write(articleInfo);
	i = i + 1
	print "-----------------------------------"
	tickerLog.close();
	tickerScores.close();
print "\nAll Done!"

