#Creating a DataFrame with YouTube comments
 def comment_WWE_YouTube_DataFrame(URL):
    #!pip install selenium
    import pandas as pd
    import time
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from bs4 import BeautifulSoup
    from bs4 import Comment
    import requests
    import re
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    
    # Variable containing the link to the video to scrape
    video_to_scrape = URL

    # Chrome webdriver has been installed on the system
    driver = webdriver.Chrome()
    driver.get(video_to_scrape)

    # Amount of time on which the code waits to move on to the next comment
    scroll_pause_time = 2
    # Delay for webdriver in seconds
    delay = 5
    # True means we are still scrolling; False means we are not scrolling anymore
    scrolling = True
    # The last current position on the page
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    # The list where we will save the comments
    all_comments_list = []
    # Number of attempts before we switch scrolling to False
    scrolling_attempt = 4

    def scrape_yt_comments():
        loaded_comments = []
        try:
            all_usernames = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#author-text span")))
            all_comments = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content-text")))

            for username, comment in zip(all_usernames, all_comments):
                current_comment = {"username": username.text, "comment": comment.text}
                loaded_comments.append(current_comment)
            return loaded_comments
        except Exception as e:
            print(f"Error while scraping comments: {str(e)}")
            return None

    while scrolling:
        htmlelement = driver.find_element(By.TAG_NAME, "body")
        htmlelement.send_keys(Keys.END)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            scrolling_attempt -= 1
            print(f"Scrolling attempt {scrolling_attempt}")
            if scrolling_attempt == 0:
                scrolling = False
        else:
            scrolling_attempt = 4

        last_height = new_height
        
        try:
            last_20_comments = scrape_yt_comments()
            if last_20_comments:
                all_comments_list.extend(last_20_comments)
        except Exception as e:
            print(f"Error while loading comments: {str(e)}")
    
    [user.pop('username',None) for user in all_comments_list]
    
    def get_date(url):
        url=URL
        data=requests.get(url).text
        soup=BeautifulSoup(data,'html.parser')
        test=soup.find('meta', itemprop ='datePublished')

        content_value = test.get('content')
        return content_value.split('T')[0]

    flat_list=[]
    #removing all_comments_list:
    for x in all_comments_list:
        flat_list.append(x)
    df=pd.DataFrame(flat_list)
    df['comment']=df['comment'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    df.rename(columns={'comment':'comments_{}'.format(get_date(URL))},inplace=True)
    date=pd.to_datetime(get_date(URL))
    df['Date']=date.to_period('M').to_timestamp()
    df.drop_duplicates(inplace=True)
    
    #stop_words allow us to remove words which are needed to form a proper sentence but do not provide more insight to the text
    nltk.download('stopwords')
    stop_words=set(stopwords.words('english'))
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    
    #def function to remove lower case words
    def remove_lower_case(x):
        filtered_word=[x for x in x if not re.match('^[a-z]+$', x)]
        return filtered_word
    
    #here we apply the stopwords filter on a data frame
    df['word_comment']=df.iloc[:,0].apply(lambda x: [x for x in word_tokenize(x) if x.lower() not in stop_words])
    #here we remove all lower case words
    df['word_comment_tag_words']=df['word_comment'].apply(lambda x: remove_lower_case(x))
    
    #when the compund output is bigger to equal than 0.05, then the comment will be considered as positive
    #when the compound output is smaller to equal to -0.05, the the comment will be considered as negative
    #otherwise the comment will be considerd as neutral

    def comment_sentiment(text):
        senti=SentimentIntensityAnalyzer()
        output=senti.polarity_scores(text)
        if output['compound'] >= 0.05:
            return 'Positive'
        elif output['compound'] <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    df['Sentiment']=[comment_sentiment(x) for x in df.iloc[:,0]]
    
    return df