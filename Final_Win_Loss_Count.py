#getting number of wins and losses and the different categories for the different wrestlers
def final_win_loss_count(df):
    
    def title_clean(title):
        if '(title change)' in title:
            return title.split('(')[0].strip()
        else:
            return title
        
    #getting all the wins
    win_count= df_match_card.explode('winner')
    df_win_count=win_count.groupby(['card_date_week','title(s)','champion_status','match type','winner'])['win_through'].count(
    ).reset_index().rename(columns={'title(s)':'Title Match','champion_status':'Champion Status',
                                    'match type':'Match Type','winner':'Wrestler',
                                    'win_through':'Number of Wins'})

    #test=df_win_count[df_win_count['Wrestler']=='Asuka']

    df_win_count['Number of Single Wins']=df_win_count.apply(
        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='Single Match' else 0,axis=1)

    df_win_count['Number of Triple Threat Wins']=df_win_count.apply(
        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='Triple Threat' else 0,axis=1)

    df_win_count['Number of Fata Fourway Wins']=df_win_count.apply(
        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='Fatal Fourway' else 0,axis=1)

    df_win_count['Number of Tag Team Wins']=df_win_count.apply(
        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='6 Tag Team' or x.loc['Match Type']=='Tag Team' 
        or x.loc['Match Type']=='3 Way Tag Team' else 0,axis=1)

    df_win_count['Number of Single Title Wins']=df_win_count.apply(
                                                lambda x: x.loc['Number of Wins'] if x.loc['Champion Status']=='new champion'
                                                and x.loc['Match Type']=='Single Match'
                                                and x.loc['Title Match']!='No Title Match'
                                                else 0,axis=1)

    df_win_count['Number of Tag Team Title Wins']=df_win_count.apply(
                                                lambda x: x.loc['Number of Wins'] if x.loc['Champion Status']=='new champion'
                                                and x.loc['Match Type']=='Tag Team' or x.loc['Match Type']=='6 Tag Team'
                                                and x.loc['Title Match']!='No Title Match' else 0,axis=1)

    df_win_count['Title Match']=df_win_count['Title Match'].apply(title_clean)

    df_win_count['Number of Single Title Defenses']=df_win_count.apply(
                                                lambda x: x.loc['Number of Wins'] if x.loc['Champion Status']=='still champion'
                                                and x.loc['Match Type']=='Single Match'
                                                and x.loc['Title Match']!='No Title Match'
                                                else 0,axis=1)

    df_win_count['Number of Tag Team Title Defenses']=df_win_count.apply(
                                                lambda x: x.loc['Number of Wins'] if x.loc['Champion Status']=='still champion'
                                                and x.loc['Match Type']=='Tag Team' or x.loc['Match Type']=='6 Tag Team'
                                                or x.loc['Match Type']=='3 Way Tag Team'
                                                and x.loc['Title Match']!='No Title Match' else 0,axis=1)

    df_win_count['Royal Rumble Win']=df_win_count.apply(
                                        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='Royal Rumble' else 0,axis=1)

    df_win_count['Money in the Bank Win']=df_win_count.apply(
                                        lambda x: x.loc['Number of Wins'] if x.loc['Match Type']=='Money in the Bank' else 0,
                                        axis=1)

    
    #getting all the loss
    loss_count= df_match_card.explode('loser')
    df_loss_count=loss_count.groupby(['card_date_week','title(s)','champion_status','match type','loser'])['win_through'].count(
    ).reset_index().rename(columns={'title(s)':'Title Match','champion_status':'Champion Status',
                                    'match type':'Match Type','loser':'Wrestler',
                                    'win_through':'Number of Losses'})

    #test=df_win_count[df_win_count['Wrestler']=='Asuka']

    df_loss_count['Number of Single Losses']=df_loss_count.apply(
        lambda x: x.loc['Number of Losses'] if x.loc['Match Type']=='Single Match' else 0,axis=1)

    df_loss_count['Number of Triple Threat Losses']=df_loss_count.apply(
        lambda x: x.loc['Number of Losses'] if x.loc['Match Type']=='Triple Threat' else 0,axis=1)

    df_loss_count['Number of Fata Fourway Losses']=df_loss_count.apply(
        lambda x: x.loc['Number of Losses'] if x.loc['Match Type']=='Fatal Fourway' else 0,axis=1)

    df_loss_count['Number of Tag Team Losses']=df_loss_count.apply(
        lambda x: x.loc['Number of Losses'] if x.loc['Match Type']=='6 Tag Team' or x.loc['Match Type']=='Tag Team' 
        or x.loc['Match Type']=='3 Way Tag Team' else 0,axis=1)

    df_loss_count['Number of Single Title Losses']=df_loss_count.apply(
                                                lambda x: x.loc['Number of Losses'] if x.loc['Champion Status']=='new champion'
                                                and x.loc['Match Type']=='Single Match'
                                                and x.loc['Title Match']!='No Title Match'
                                                else 0,axis=1)

    df_loss_count['Number of Tag Team Title Losses']=df_loss_count.apply(
                                                lambda x: x.loc['Number of Losses'] if x.loc['Champion Status']=='new champion'
                                                and x.loc['Match Type']=='Tag Team' or x.loc['Match Type']=='6 Tag Team'
                                                and x.loc['Title Match']!='No Title Match' else 0,axis=1)

    df_loss_count['Title Match']=df_loss_count['Title Match'].apply(title_clean)
    
    df_final_count=df_win_count.merge(df_loss_count,how='left',on=
                                  ['card_date_week','Title Match','Champion Status','Match Type','Wrestler'])

    adjust_col=list(df_final_count.columns[5:])
    for x in adjust_col:
        df_final_count[x]=df_final_count[x].fillna(0).astype(int)

    df_final_count['Overall Number of Matches']=df_final_count['Number of Wins'] + df_final_count['Number of Losses']
    
    return df_final_count