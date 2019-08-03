The project performs sentiment analysis on financial news articles. The input is a company ticker, and the result is a score from the range [-1, 1]. The score reflects what kind of sentiment the articles have for the company. 
The program, once it receives a specific ticker, will search for articles of that ticker in top financial news sites, such as Google Finance, Yahoo! Finance, and download articles of the past 30 days from the current date.
The downloaded articles will be cleaned and converted from HTML format to a text format, eliminating all advertisements, links, and information that are not directly related to the article itself.
Once the files are cleaned and converted from HTML to Text files, we will perform sentence splitting, part of speech tagging, and named entity recognition on all the articles downloaded.
Then, the program goes over all the sentences that refer to the ticker and checks if it has positive or negative impact on the article, these sentences or part of sentences will be marked as dark red for very bad sentiment, red for bad sentiment, green for good sentiment, and light green for very good sentiment. Based on these sentiments we will provide a score to each article.

Anaphora resolution is partially done. We noticed that most of the articles don’t use “they” or “it” to refer to the company, but there is some use of “the company” to refer to the company being checked; so, we checked only if “the company” phrases refer to the company being checked. If so, then all of the sentences that contain this phrase in it are checked.
Once everything is done for all articles, the results are presented as HTML pages. The Main HTML file will include a table consisting of all companies we’ve worked on and the calculated score of the sentiment analysis of all articles harvested and analyzed. Each ticker will link to another file that includes all articles related to that specific ticker, with their scores. Finally, each article name will link back to the article itself, where the article’s related sentences are tagged by the proper color if deemed to provide negative or positive sentiment for the company.

We have decided to implement 5 different levels of analysis instead of the regular three:
- Very Negative: score of -2
- Negative: score of -1
- Neutral: score of 0; will not affect the final score
- Positive: score of 1
- Very Positive: score of 2 \\
The sentiment analyzer looks for patterns as well as events.

System Architecture:\\
Crawling:
- Contacting main financial news article hubs, such as Google Finance, or Yahoo! Finance, and downloading relevant article URLs, and their dates of the last 30 days, for each ticker, from every website, depending on input.
- For each ticker, reading the URL list from these sites and creating a list saving the URL and date of each URL as well as its title for further use by the cleaner (aka pre-processing stage).

Pre-Processing:
- Reading each HTML file, deleting irrelevant parts, such as menus, comments section, Java Script functions, CSS blocks, and advertisements.
- Converting the cleaned HTML to regular text, by removing all the HTML tags from it, and fixing spacing and paragraph splitting.
Linguistic Analysis:
- Parsing each text file, to identify relevant sentences for each company, and tagging each sentence related to the company, with appropriate score, ranging from very negative to very positive.

Scoring:
- Each document, after being analyzed and each relevant sentence tagged, a final score of all articles is calculated based on these tags. The score is from [-1, 1]. Where +1 is very good sentiment for the company in that article, and -1 is a very bad sentiment for the company in that article.
- Once each article is scanned for negative and positive sentiment, we calculate the final score of the company using these values, where events get a double effect than regular positive or negative sentences. The score is calculated using the formula taught in class.

Presentation:
- Once everything is done, the results will be viewed in an easy to see way with proper links backtracking to the articles themselves.
- Main page includes company name, company ticker, and the calculated score for the company.
- Each line will link to all articles of that specific company, where a list of article and score can be seen. There, each article name will link to the tagged article itself.

Project Modules:
- Crawler.py: given command line input, downloads the links to articles of ticker(s) from a specific site.
- Cleaner.py: links downloaded by the crawler, are downloaded, cleaned, and saved in text format.
- SentimentAnalyzer.py: performs sentiment analysis on the articles downloaded by the cleaner, according to patterns and events. Sentences that have sentiment for the examined ticker are tagged, and statistics of how many sentences were found of each of the 4 levels are saved. Anaphora resolution is performed for “the company” phrases.
- Presenter.py: calculated the final score of each ticker based on the results given by the previous section, and creates HTML files to present the results (tickers and their scores, and HTML files of the tagged articles).

Requirements:
- Python 2.6.4: http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi
- BeautifulSoup v3.0.8: http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.8.tar.gz
- Nltk package, stemmer, part of speech tagger, sentence splitter, tokenizer packages.
- companyList.txt: contains lines, in each line a pair of the format: “Ticker:CompanyName” for the 10 companies in our list:
- MRK:Merck & Co Inc
- C:Citigroup Inc
- DIS:Walt Disney Co
- NOK:Nokia
- GS:Goldman Sachs Group Inc
- POT:Potash Corp of Saskatchewan Inc
- KMB:Kimberly-Clark Corp
- LVS:Las Vegas Sands Corp
- INTC:Intel Corp
- AA:Alcoa Inc