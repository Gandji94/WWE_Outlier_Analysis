#Getting a DataFrame with the Word Count of Wrestlers
def Wrestler_Comment_Count(dataframe,URL):
    import pandas as pd
    from collections import Counter
    from bs4 import BeautifulSoup
    from bs4 import Comment
    import requests
    
    def get_date(url):
        url=URL
        data=requests.get(url).text
        soup=BeautifulSoup(data,'html.parser')
        test=soup.find('meta', itemprop ='datePublished')

        content_value = test.get('content')
        return content_value.split('T')[0]
    
    step_list=[x for lst in dataframe.iloc[:,3] for x in lst]
    df_count=Counter(step_list)
    df_count_dict=dict(df_count)
    sorted_word_count=dict(sorted(df_count_dict.items(),key=lambda item:item[1],reverse=True))
    
    df_app=pd.DataFrame(sorted_word_count.items(),columns=['Word','Count'])
    date=pd.to_datetime(get_date(URL))
    df_app['Date']=date
    #how to filter out non-string values
    df_app['Word']=df_app['Word'][df_app['Word'].apply(lambda x: x.isalpha())]
    df_app['Word']=df_app['Word'].astype(str)
    df_app=df_app[df_app['Word']!='nan']
    
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
    df_app['Wrestler'] = df_app['Word'].map(lambda x: find_key(wrestler_dict, x))
    #this line allows us to remove the list from each value, otherwise the "Wrestler" column would have 
    df_app['Wrestler'] = df_app['Wrestler'].apply(lambda x: x[0] if isinstance(x, list) else x)
    date=pd.to_datetime(get_date(URL))
    df_app['Month_Date']=date.to_period('M').to_timestamp()
    return df_app