#getting the dataframe for the match cards for Python
def mach_card_df(max_pages):
    import pandas as pd
    import numpy as np
    import sys as sys
    import matplotlib.pyplot as plt
    import seaborn as sns
    from bs4 import BeautifulSoup
    from bs4 import Comment
    import requests
    import re
    from statistics import mode
    
    def match_type(row):
        match = row['match']
        match_2 = row['match.2']
        match_type=row['match type']
        
        #how to lookup if a value is in a PandasSeries included
        if '&' in match and len(match.split('&')) ==2:
            return 'Tag Team'
        elif '&' in match and len(match.split('&')) ==3:
            return '6 Tag Team'
        elif '&' in match_2 and len(match.split('&'))==4:
            return '3 Way Tag Team'
        elif ',' in match_2 and len(match_2.split(',')) == 2:
            return 'Triple Threat'
        elif ',' in match_2 and len(match_2.split(',')) ==3:
            return 'Fatal Fourway'
        elif ',' in match_2 and len(match_2.split(',')) ==5:
            return 'Elimination Chamber/Gauntlet Match'
        elif ',' in match_2 and len(match_2.split(',')) <= 8:
            return 'Money in the Bank'
        elif ',' in match_2 and len(match_2.split(',')) <=26:
            return 'Battle Royal/Andre The Giant Memorial'
        elif ',' in match_2 and len(match_2.split(',')) ==29:
            return 'Royal Rumble'
        else:
            return 'Single Match'

    #getting the match duration in seconds
    def match_duration(row):
        if pd.isna(row['duration']):
            return np.nan
        else:
            return int(row['duration'].split(':')[0])*60 + int(row['duration'].split(':')[1])

    #getting the championship status
    def champion_status(title):
        if '(title change)' in title:
            return 'new champion'
        elif '(2016)' in title:
            steps=title.split('(')
            if len(steps) >2:
                step=steps[2]
                if 'title change)' in step:
                    return 'new champion'
                else:
                    return 'still champion'
            else:
                return 'still champion'
        elif 'No Title Match' in title:
            return 'No Title Match'
        else:
            return 'still champion'
        
    def champ(row):
        title=row['title(s)']
        wrestler=row['winner']
        other_wrestler=row['loser']
        champ_status=row['champion_status']
        win=row['win_through']
        if 'No Title Match' in title:
            return 'No Champion'
        else:
            if champ_status =='still champion' or win=='DQ':
                return wrestler
            elif champ_status =='new champion':
                return wrestler
            else:
                return other_wrestler
            
    def name_clean_winner(row):
        wrestler=row['winner']
        if '(c)' in wrestler:
            wrestler_parts=wrestler.split('(')
            if len(wrestler_parts) <= 2:
                return wrestler.split('(')[0].split('\xa0')[0]
            else:
                wrst=[]
                wrst.append(wrestler.split("(")[0].split('\xa0')[0])
                wrst.append(wrestler.split('(')[1].split('&')[1].split('\xa0')[0])
                return wrst
        elif '(c)' not in wrestler and '&' not in wrestler and len(wrestler)<=250:
            return wrestler
        else:
            if '&' in wrestler:
                tag_parts=wrestler.split('&')
                if len(tag_parts) <3:
                    tag_team_win=[]
                    tag_team_win.append(tag_parts[0].strip())
                    tag_team_win.append(tag_parts[1].strip())
                    return tag_team_win
                else:
                    tag_team_win=[]
                    for x in range(0,len(tag_parts)):
                        tag_team_win.append(tag_parts[x].strip())
                    return tag_team_win
            else:
                tag_parts=wrestler.split('&')
                tag_team_win=[]
                for x in range(0,len(tag_parts)):
                    tag_team_win.append(tag_parts[x].strip())
                return tag_team_win
    
    #this def function includes other 
    def name_clean_loser(row):
        other_wrestler=row['loser']
        if '(c)' in other_wrestler:
            other_wrestler_parts=other_wrestler.split('(')
            if len(other_wrestler_parts) <= 2:
                return other_wrestler.split('(')[0].split('\xa0')[0]
            else:
                wrst_other=[]
                wrst_other.append(other_wrestler.split("(")[0].split('\xa0')[0])
                wrst_other.append(other_wrestler.split('(')[1].split('&')[1].split('\xa0')[0])
                return wrst_other
        elif '(c)' not in other_wrestler and '&' not in other_wrestler and len(other_wrestler)<=250:
            return other_wrestler
        else:
            if '&' in other_wrestler:
                tag_parts=other_wrestler.split('&')
                if len(tag_parts) <3:
                    tag_team_loss=[]
                    tag_team_loss.append(tag_parts[0].strip())
                    tag_team_loss.append(tag_parts[1].strip())
                    return tag_team_loss
                else:
                    tag_team_loss_6=[]
                    for x in range(0,len(tag_parts)):
                        tag_team_loss_6.append(tag_parts[x].strip())
                    return tag_team_loss_6
            elif ',' in other_wrestler:
                new_wrest=[]
                wrest=other_wrestler.split(',')
                for w in wrest:
                    w=w.strip()
                    new_wrest.append(w)
                return new_wrest
            else:
                tag_parts=other_wrestler.split('&')
                tag_team_loss_6=[]
                for x in range(0,len(tag_parts)):
                    tag_team_loss_6.append(tag_parts[x].strip())
                return tag_team_loss_6
    
    #this for-loop will get us all the match cards that took place in
    num=max_pages
    num=int(num)
    wp_links=[]
    for x in range(1,num):
        data=requests.get('http://www.profightdb.com/cards/wwe-cards-pg{}-no-2.html?order=&type='.format(x)).text
        soup=BeautifulSoup(data,'html.parser')
        table=soup.find('div', class_='table-wrapper')
        if table:
            link_ele=table.find_all('a',href=re.compile(r'^/cards/wwe/'))
            for x in link_ele:
                wp_links.append(x['href'])
    #wp_links=wp_link[6:]

    match_card1=pd.read_html(
    'http://www.profightdb.com/cards/wwe/friday-night-smackdown---wrestlemania-smackdown-52602.html')[1]
    match_card1['match type']=match_card1.apply(match_type,axis=1)
    match_card1['match duration_sec']=match_card1.apply(match_duration,axis=1)
    match_card1['rating']=match_card1['rating'].fillna('-')
    match_card1['title(s)']=match_card1['title(s)'].fillna('No Title Match')
    match_card1.drop(columns=['no.','duration'],inplace=True)
    match_card1['match.1'].replace({'def.':'victory','def. (pin)':'pinfall',
                                   'def. (sub)':'submission','def. (DQ)':'DQ'},inplace=True)
    match_card1.rename(columns={'match':'winner','match.1':'win_through','match.2':'loser'},inplace=True)
    date=pd.read_html(
        'http://www.profightdb.com/cards/wwe/friday-night-smackdown---wrestlemania-smackdown-52602.html'
        )[0].iloc[0,0].split(',')[1]
    match_card1['card_date']=pd.to_datetime(date)
    match_card1['card_date_month']=pd.to_datetime(date).to_period('M').to_timestamp()
    match_card1['winner'].replace({'A.J. Styles': 'AJ Styles','L.A. Knight':'LA Knight'}, inplace=True)
    match_card1['loser'].replace({'A.J. Styles': 'AJ Styles','L.A. Knight':'LA Knight'}, inplace=True)
    df_match_card=match_card1

    for x in wp_links:
        match_card=pd.read_html(
        'http://www.profightdb.com{}'.format(x))[1]
        match_card['match type']=match_card.apply(match_type,axis=1)
        match_card['match duration_sec']=match_card.apply(match_duration,axis=1)
        match_card['rating']=match_card['rating'].fillna('-')
        match_card['title(s)']=match_card['title(s)'].fillna('No Title Match')
        match_card.drop(columns=['no.','duration'],inplace=True)
        match_card['match.1'].replace({'def.':'victory','def. (pin)':'pinfall',
                                       'def. (sub)':'submission','def. (DQ)':'DQ'},inplace=True)
        match_card.rename(columns={'match':'winner','match.1':'win_through','match.2':'loser'},inplace=True)
        match_card['winner'].replace({'A.J. Styles': 'AJ Styles','L.A. Knight':'LA Knight'}, inplace=True)
        match_card['loser'].replace({'A.J. Styles': 'AJ Styles','L.A. Knight':'LA Knight'}, inplace=True)
        date=pd.read_html('http://www.profightdb.com{}'.format(x))[0].iloc[0,0].split(',')[1]
        match_card['card_date']=pd.to_datetime(date)
        match_card['card_date_month']=pd.to_datetime(date).to_period('M').to_timestamp()
        df_match_card=pd.concat([df_match_card,match_card])
    
    #when we can not use the mode for the particular title match, we use the overall mode
    stand_dur_val = round(df_match_card['match duration_sec'].describe().iloc[4])
    titles=list(df_match_card['title(s)'].unique())
    for title in titles:
        title_filter = df_match_card['title(s)'] == title
        if title_filter.any():  # Check if any value is True
            mode_val = None #we assume before the loop is executed model_val is equal to None, so we can check if it is after
            ##the loop still None
            filtered_data = df_match_card[(title_filter) & (~pd.isna(df_match_card['match duration_sec']))]
            if not filtered_data.empty:  # Check if the filtered DataFrame is not empty
                mode_val = round(filtered_data['match duration_sec'].agg(mode))
            if mode_val is not None: #Check if model_val is still None
                df_match_card.loc[title_filter, 'match duration_sec'] = df_match_card.loc[
                    title_filter, 'match duration_sec'].fillna(mode_val)
            else: #else we fill the NaN values with the overall mode when we were able to generate any
                df_match_card.loc[title_filter, 'match duration_sec'] = stand_dur_val
        else: #the same here
            df_match_card.loc[title_filter, 'match duration_sec'] = stand_dur_val
    df_match_card['match duration_sec']=df_match_card['match duration_sec'].astype(int)
    df_match_card['winner']=df_match_card.apply(name_clean_winner,axis=1)
    df_match_card['loser']=df_match_card.apply(name_clean_loser,axis=1)
    df_match_card['champion_status'] = df_match_card['title(s)'].apply(champion_status)
    df_match_card['champion']=df_match_card.apply(champ,axis=1)
    df_match_card['card_date_week']=df_match_card['card_date'].apply(lambda x:pd.to_datetime(x).to_period('W').to_timestamp())
    return df_match_card

df_match_card=mach_card_df(input('Please enter the number of the last page number: '))