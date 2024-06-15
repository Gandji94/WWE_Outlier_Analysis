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
    scroll_pause_time = 3
    # Delay for webdriver in seconds
    delay = 5
    # True means we are still scrolling; False means we are not scrolling anymore
    scrolling = True
    # The last current position on the page
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    # The list where we will save the comments
    all_comments_list = []
    # Number of attempts before we switch scrolling to False
    scrolling_attempt = 3

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
            scrolling_attempt = 2

        last_height = new_height

        try:
            last_20_comments = scrape_yt_comments()
            if last_20_comments:
                all_comments_list.extend(last_20_comments)
        except Exception as e:
            print(f"Error while loading comments: {str(e)}")

    [user.pop('username',None) for user in all_comments_list]

    def get_date(url):
        
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
    if df.empty:
        print("DataFrame is empty.")
        return df #this section allows us to stop/return and an empty dataframe so the loop can continue
    
    # Apply function to clean comments
    df['comment'] = df['comment'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    # Rename column based on date
    #df.rename(columns={'comment': 'comments_{}'.format(get_date(URL))}, inplace=True)
    # Convert date to datetime
    df['Date']=pd.to_datetime(get_date(URL))
    date = pd.to_datetime(get_date(URL))
    df['Date_Month'] = date.to_period('M').to_timestamp()
    # Drop duplicates
    df.drop_duplicates(inplace=True)
    
    #stop_words allow us to remove words which are needed to form a proper sentence
    #but do not provide more insight to the text
    nltk.download('stopwords')
    stop_words=set(stopwords.words('english'))
    nltk.download('punkt')
    nltk.download('vader_lexicon')

    #def function to remove lower case words
    def remove_lower_case(x):
        filtered_word=[x for x in x if not re.match('^[a-z]+$', x)]
        return filtered_word

    #here we apply the stopwords filter on a data frame
    df['word_comment'] = df['comment'].apply(lambda x: [x for x in word_tokenize(x) if x.lower() not in stop_words])
    #here we remove all lower case words
    df['word_comment_tag_words'] = df['word_comment'].apply(lambda x: remove_lower_case(x))

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
    
    #start of creating the count dataframe
    df_counts=df[['word_comment_tag_words', 'Sentiment','Date','Date_Month']]
    #exploded() allows us to remove values from a list
    df_count_exploded=df_counts.explode('word_comment_tag_words')
    #with groupby() we are able to generate a count based on sentiment, wrestler and dates
    df_count = df_count_exploded.groupby(['Sentiment',
                    'word_comment_tag_words',
                    'Date',
                    'Date_Month']).size().reset_index(name='Count').sort_values('Count',ascending=False)
    #isalpha() makes sure to filter out all non-string values
    df_count['word_comment_tag_words']=df_count['word_comment_tag_words'][df_count['word_comment_tag_words'].apply(
        lambda x: x.isalpha())]

    url="https://www.thesmackdownhotel.com/roster/?promotion=wwe&date=all-time"
    data=requests.get(url).text
    soup=BeautifulSoup(data,'html.parser')
    #getting the section where the needed information is loacted
    test=soup.find('div', class_ ='roster_section roster2k22')
    #list comprehension to get all Names
    wrestler=[x.get('title') for x in test.find_all('a')]

    #splitting each string value by the space
    name_split=[x.split(' ') for x in wrestler]
    #nested list comprehension
    plural_name_split = [[k + 's' for k in x.split(' ')] for x in wrestler]
    #splitting each string value by the space and truning all string values into lower case
    lower_name_split=[x.lower().split(' ') for x in wrestler]
    #nested list comprehension
    plural_lower_name_split=[[k + "s" for k in x.lower().split(' ')] for x in wrestler]
    #putting each string value from a list into a list of its own
    sep_list=[[str(x)] for x in wrestler]
    #nested list comprehension
    plural_sep_list=[[k + 's' for k in [str(x)]] for x in wrestler]
    #putting each string value from a list into a list of its own and transforming all letter to lower case
    sep_list_lower=[[str(x.lower())] for x in wrestler]

    plural_lower_sep_list=[[k + "s" for k in [str(x.lower())]] for x in wrestler]

    dict_value=[]
    for x in range(0,len(wrestler)):
        new_input=sep_list[x]+plural_sep_list[x]+sep_list_lower[x]+plural_lower_sep_list[x]+name_split[x]+plural_name_split[x]
        dict_value.append(new_input)

    wrestler_dict=dict(zip(wrestler,dict_value))

    del wrestler_dict['Aalyah Mysterio'][5]
    del wrestler_dict['Aalyah Mysterio'][6]
    del wrestler_dict['AJ Lee'][4]
    del wrestler_dict['AJ Lee'][5]
    del wrestler_dict['The Rock'][4]
    del wrestler_dict['The Rock'][5]
    del wrestler_dict['The Miz'][4]
    del wrestler_dict['The Miz'][5]
    del wrestler_dict['The Undertaker'][4]
    del wrestler_dict['The Undertaker'][5]
    del wrestler_dict['John Morrison'][4]
    del wrestler_dict['John Morrison'][5]
    del wrestler_dict['Austin Theory'][4]
    del wrestler_dict['Austin Theory'][5]
    del wrestler_dict['Dominik Mysterio'][5]
    del wrestler_dict['Dominik Mysterio'][6]
    del wrestler_dict['Chris Benoit'][0]
    del wrestler_dict['Chris Benoit'][0]
    del wrestler_dict['Chris Benoit'][0]
    del wrestler_dict['Chris Benoit'][0]
    del wrestler_dict['Chris Benoit'][0]
    del wrestler_dict['Chris Benoit'][1]
    first_val=['Adam Cole','Adam Pearce','Adam Rose','Angel Hayze','Austin Aries','Bam Neely','Big Boss Man','Big Cass','Big Daddy V',
              'Big John Studd','Big Show','Billy Kidman','Bill Watts','Blake Beverly','Bobby Fish','Bobby Heenan','Chris Candido',
              'Chris Kanyon','Chris Masters','Chris Park','Drake Maverick','Duke Droese','Eddie Dennis','Eddie Gilbert','Eddie Graham',
              'Eric Bischoff','Jeff Hardy','Jeff Jarrett','Jimmy Hart','Jimmy Jacobs','Jimmy Smith','Jimmy Snuka','Kevin Nash','Randy Savage',
              'Rob Conway','Rob Gronkowski','Shawn Daivari','Shawn Spears','Shawn Stasiak','Luther Reigns','Rocco Rock','Drew Gulak',
              'John Laurinaitis','Linda McMahon','Mr. Stone']
    for x in first_val:
        del wrestler_dict[x][4:]
    wrestler_dict['WWE']=['WWE','wwe']
    wrestler_dict['Raw']=['RAW','Raw','raw']
    wrestler_dict['Smack Down']=['Smack Down','smack down','Smack down','Smack','smack','Down','down','Smackdown','SmackDown',
                                'smackdown']
    wrestler_dict['WrestleMania']=['WrestleMania','wrestlemania','WM','wm','Wrestlemania','Mania','mania']
    wrestler_dict['Royal Rumble']=['Royal Rumble','royal rumble','RR','rr','Royal rumble']
    wrestler_dict['Elimination Chamber']=['Elimination Chamber','elimination chamber','EC','ec','Elimination chamber']
    wrestler_dict['NXT Vengeance Day']=['Vengeance Day','vengeance day']
    wrestler_dict['NXT Roadblock']=['Roadblock','roadblock']
    wrestler_dict['NXT Stand & Deliver']=['Stand & Deliver','stand & deliver']
    wrestler_dict['Backlash']=['Backlash','backlash']
    wrestler_dict['NXT Battleground']=['Battleground','battleground']
    wrestler_dict['Money in the Bank']=['Money in the Bank','vengeance day','money in the bank','MITB','mitb']
    wrestler_dict['NXT Heatwave']=['Heatwave','heatwave']
    wrestler_dict['Summer Slam']=['Summer Slam','summer slam']
    wrestler_dict['Bash in Berlin']=['Bash in Berlin','bash in berlin','BIB','bib']
    wrestler_dict['Survivor Series']=['Survivor Series','survivor series','Survivor series']
    wrestler_dict['The Bloodline']=['Bloodline','bloodline','The Bloodline','the bloodline']
    wrestler_dict['The Judgment Day']=['The Judgment Day','the judgment day','Judgment Day','judgment day', 'Judgment','judgment',
                                      'Day','day']
    wrestler_dict['Seth Rollins']=['Seth Rollins','Seth Rollinss','Seth','Seth ','Seths','seth','seths','Rollins','rollins','Rollinss','rollinss']
    wrestler_dict['McMahon']=['McMahon','mcmahon','Mcmahon','mcMahon','McMahons','mcmahons','Mcmahons','mcMahons']
    wrestler_dict['Golden Era']=['Golden Era','golden era','Golden','golden']
    wrestler_dict['Attitude Era']=['Attitude Era','attitude era','Attitude','attitude','Era','era']
    wrestler_dict['Ruthless Aggression Era']=['Ruthless Aggression Era','ruthless aggression era',
                                              'Ruthless','ruthless','Aggression','aggression',]
    wrestler_dict['PG Era']=['PG Era','pg era','PG','pg']
    wrestler_dict['New Era']=['New Era','new era','New','new']
    wrestler_dict['The Rock'].append('Dwayne')
    wrestler_dict['The Rock'].append('Dwaynes')
    wrestler_dict['The Rock'].append('dwayne')
    wrestler_dict['The Rock'].append('dwaynes')
    del wrestler_dict['Seth ']
    wrestler_dict['Stone Cold Steve Austin']=wrestler_dict['Steve Austin']
    del wrestler_dict['Steve Austin']
    wrestler_dict['Stone Cold Steve Austin'].append('Stone')
    wrestler_dict['Stone Cold Steve Austin'].append('Stones')
    wrestler_dict['Stone Cold Steve Austin'].append('stone')
    wrestler_dict['Stone Cold Steve Austin'].append('stones')
    wrestler_dict['Stone Cold Steve Austin'].append('Cold')
    wrestler_dict['Stone Cold Steve Austin'].append('Colds')
    wrestler_dict['Stone Cold Steve Austin'].append('cold')
    wrestler_dict['Stone Cold Steve Austin'].append('colds')
    wrestler_dict['Stone Cold Steve Austin'].append('Stone Cold')
    wrestler_dict['Stone Cold Steve Austin'].append('Stone Colds')
    wrestler_dict['Stone Cold Steve Austin'].append('Stone cold')
    wrestler_dict['Stone Cold Steve Austin'].append('Stone colds')
    wrestler_dict['Stone Cold Steve Austin'].append('stone cold')
    wrestler_dict['Stone Cold Steve Austin'].append('stone cold')
    wrestler_dict['Shawn Michaels'].append('HBK')
    wrestler_dict['Shawn Michaels'].append('HBKs')
    wrestler_dict['Shawn Michaels'].append('hbk')
    wrestler_dict['Shawn Michaels'].append('hbks')
    del wrestler_dict["Paul "]
    wrestler_dict['Triple H']=['Triple H','Triple Hs','triple h','triple hs','Triple','Triples','triple','triples','H','Hs',
                              'h','hs','HHH','HHHs','hhh','hhhs','Hunter','Hunters','hunter','hunters']

    #def function to get the key for the corrosponding value
    def find_key(dictionary, value):
        keys = []
        for key, val in dictionary.items():
            if value in val:
                keys.append(key)
        return keys if keys else None  # If no matching keys found, return None

    #mapping the column values to the matching dictionary values
    df_count['word_comment_tag_words'] = df_count['word_comment_tag_words'].map(lambda x: find_key(wrestler_dict, x))
    #this line allows us to remove the list from each value, otherwise the "Wrestler" column would have 
    df_count['word_comment_tag_words'] = df_count['word_comment_tag_words'].apply(lambda x: x[0] if isinstance(x, list) else x)
    df_count.rename(columns={'word_comment_tag_words':'Wrestler'},inplace=True)

    return df,df_count