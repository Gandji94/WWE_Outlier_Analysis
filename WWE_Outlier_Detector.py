#Outlier Detection
def outlier_wrestler(match,sent):
    from sklearn.ensemble import IsolationForest
    from sklearn.svm import OneClassSVM
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import RobustScaler

    df_total=pd.read_csv(r"C:\Users\gandj\OneDrive\Desktop\Case_Study\WWE\Number_of_Wins_Losses_Sentiment_Count.csv").iloc[:,1:]

    df_total_month=df_total.groupby(['Date_Month','Wrestler'])[['Number of Wins', 'Number of Single Wins',
           'Number of Triple Threat Wins', 'Number of Fata Fourway Wins',
           'Number of Tag Team Wins', 'Number of Single Title Wins',
           'Number of Tag Team Title Wins', 'Number of Single Title Defenses',
           'Number of Tag Team Title Defenses', 'Royal Rumble Win',
           'Money in the Bank Win', 'Number of Losses', 'Number of Single Losses',
           'Number of Triple Threat Losses', 'Number of Fata Fourway Losses',
           'Number of Tag Team Losses', 'Number of Single Title Losses',
           'Number of Tag Team Title Losses','Positive Count','Neutral Count','Negative Count']].sum().reset_index()

    df_feat_outl=df_total_month

    if sent=='Positive Count':
        df_feat_outl=df_feat_outl[df_feat_outl['Positive Count'] > df_feat_outl['Negative Count']]
    else:
        df_feat_outl=df_feat_outl[df_total_month['Positive Count'] < df_feat_outl['Negative Count']]

    #Support Vector Machine
    X=df_feat_outl[[match,sent]].values
    robust_X=RobustScaler().fit_transform(X)

    param_kernel=[]
    param_degree=[]
    param_coef=[]
    param_gamma=[]
    param_tol=[]
    param_nu=[]
    best_score_svm=[]

    for kernel in ['linear','poly','rbf','sigmoid']:
        for degree in np.unique(np.linspace(1,5,dtype=int)):
            for coef in np.linspace(0.0,1.0,5,dtype=float):
                for gamma in ['scale','auto']:
                    for tol in np.linspace(0.0001,0.1,5,dtype=float):
                        for nu in np.linspace(0.1,0.5,5,dtype=float):
                            try:
                                SVM_Class=OneClassSVM(kernel=kernel,degree=degree,coef0=coef,gamma=gamma,tol=tol,nu=nu).fit_predict(robust_X)
                                best_score_svm.append(round(silhouette_score(X,SVM_Class),5))
                                param_kernel.append(kernel)
                                param_degree.append(degree)
                                param_coef.append(coef)
                                param_gamma.append(gamma)
                                param_tol.append(tol)
                                param_nu.append(nu)
                            except ValueError as e:
                                #print(f"Skipping combination due to error: {e}")
                                continue

    best_value_svm=best_score_svm.index(max(best_score_svm))

    SVM_Class_Vis=OneClassSVM(kernel=param_kernel[best_value_svm],
                          degree=param_degree[best_value_svm],
                          coef0=param_coef[best_value_svm],
                          gamma=param_gamma[best_value_svm],
                          tol=param_tol[best_value_svm],
                          nu=param_nu[best_value_svm]).fit_predict(robust_X)
    s_score_svm=round(silhouette_score(X,SVM_Class_Vis),5)


    #Isolation Forest
    param_n_estimator=[]
    param_max_samples=[]
    param_max_features=[]
    param_bootstrap=[]
    best_score_IsoForest=[]


    #contamination=0.01=> only 1 percent of the data should be
    for n_estimator in [50,100,200,300,500]:
        for max_samples in ['auto',50,100,200,300,500]:
                for max_features in np.linspace(0.1,1,5,dtype=float):
                    for bootstrap in [True,False]:
                        IsoPred=IsolationForest(n_estimators=n_estimator, max_samples=max_samples, contamination=0.01,
                                                max_features=max_features, bootstrap=bootstrap,random_state=101).fit_predict(X)
                        best_score_IsoForest.append(round(silhouette_score(X,IsoPred),5))
                        param_n_estimator.append(n_estimator)
                        param_max_samples.append(max_samples)
                        param_max_features.append(max_features)
                        param_bootstrap.append(bootstrap)

    best_value_IsoForest=best_score_IsoForest.index(max(best_score_IsoForest))

    IsoPred_Vis=IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                max_samples=param_max_samples[best_value_IsoForest],
                                contamination=0.01,
                                max_features=param_max_features[best_value_IsoForest],
                                bootstrap=param_bootstrap[best_value_IsoForest],
                                random_state=101).fit_predict(X)
    s_score_IsoFor=round(silhouette_score(X,IsoPred_Vis),5)

    #creating the dataframe to check which model performs the best
    df_outcome=pd.DataFrame({'Score':[s_score_svm,s_score_IsoFor]},index=['Support Vector Machine',
                'Isolation Forest']).reset_index().rename(columns={'index':'Model'})


    if not df_outcome.empty and df_outcome[df_outcome['Score'] == df_outcome['Score'].max()].iloc[0]['Model'] == 'Support Vector Machine':
        SVM_Class_Vis=OneClassSVM(kernel=param_kernel[best_value_svm],
                          degree=param_degree[best_value_svm],
                          coef0=param_coef[best_value_svm],
                          gamma=param_gamma[best_value_svm],
                          tol=param_tol[best_value_svm],
                          nu=param_nu[best_value_svm]).fit_predict(robust_X)
        s_score_svm=round(silhouette_score(X,SVM_Class_Vis),5)
        print("Silhouette score for the Support Vector Machine model is: {}".format(s_score_IsoFor))

        SVM_Class=OneClassSVM(kernel=param_kernel[best_value_svm],
                              degree=param_degree[best_value_svm],
                              coef0=param_coef[best_value_svm],
                              gamma=param_gamma[best_value_svm],
                              tol=param_tol[best_value_svm],
                              nu=param_nu[best_value_svm]).fit(robust_X)

        df_feat_outl['{}_{}_SVM'.format(match,sent)] = SVM_Class.decision_function(robust_X)
        if len(df_feat_outl[df_feat_outl['{}_{}_SVM'.format(match, sent)] < 0]) > (len(df_feat_outl['{}_{}_SVM'.format(match, sent)])*0.1):
            df_feat_outl['{}_{}_SVM'.format(match,sent)] = SVM_Class.decision_function(robust_X)*-1
            df_feat_outl['{}_{}_SVM_Rank'.format(match,sent)] = df_feat_outl['{}_{}_SVM'.format(match,sent)].rank()
            outliers_df = df_feat_outl[df_feat_outl['{}_{}_SVM'.format(match, sent)] < 0]
            
            SVM_Class_Vis=OneClassSVM(kernel=param_kernel[best_value_svm],
                          degree=param_degree[best_value_svm],
                          coef0=param_coef[best_value_svm],
                          gamma=param_gamma[best_value_svm],
                          tol=param_tol[best_value_svm],
                          nu=param_nu[best_value_svm]).fit_predict(robust_X)*-1
            
            outlier_index=np.where(SVM_Class_Vis==-1)
            
            if not outliers_df.empty:
                display(outliers_df[['Date_Month','Wrestler']])
            else:
                print('No outliers found.')
            outlier_index=np.where(SVM_Class_Vis==-1)
            outlier_values=X[outlier_index]
            sns.scatterplot(x=X[:,0], y=X[:,1])
            sns.scatterplot(x=outlier_values[:,0], y=outlier_values[:,1], color='r')
            plt.ylabel(sent)
            plt.xlabel(match)
            plt.title('Outlier Detection Support Vector Machine {} - {}'.format(match,sent))
            plt.show()
        else:
            df_feat_outl['{}_{}_SVM_Rank'.format(match,sent)] = df_feat_outl['{}_{}_SVM'.format(match,sent)].rank()
            outliers_df = df_feat_outl[df_feat_outl['{}_{}_SVM'.format(match, sent)] < 0]
            
            if not outliers_df.empty:
                display(outliers_df[['Date_Month','Wrestler']])
            else:
                print('No outliers found.')
            
            SVM_Class_Vis=OneClassSVM(kernel=param_kernel[best_value_svm],
                          degree=param_degree[best_value_svm],
                          coef0=param_coef[best_value_svm],
                          gamma=param_gamma[best_value_svm],
                          tol=param_tol[best_value_svm],
                          nu=param_nu[best_value_svm]).fit_predict(robust_X)
            
            outlier_index=np.where(SVM_Class_Vis==-1)
            outlier_values=X[outlier_index]
            
            sns.scatterplot(x=X[:,0], y=X[:,1])
            sns.scatterplot(x=outlier_values[:,0], y=outlier_values[:,1], color='r')
            plt.ylabel(sent)
            plt.xlabel(match)
            plt.title('Outlier Detection Support Vector Machine {} - {}'.format(match,sent))
            plt.show()

    else:
        IsoPred_Vis=IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                max_samples=param_max_samples[best_value_IsoForest],
                                contamination=0.01,
                                max_features=param_max_features[best_value_IsoForest],
                                bootstrap=param_bootstrap[best_value_IsoForest],
                                random_state=101).fit_predict(X)
        s_score_IsoFor=round(silhouette_score(X,IsoPred_Vis),5)
        print("Silhouette score for the Isolation Forest model is: {}".format(s_score_IsoFor))
        
        
        
        outlier_index=np.where(IsoPred_Vis==-1)[0]
        outlier_values=X[outlier_index]
        
        df_feat_outl['{}_{}_IsoFor'.format(match,sent)]=(IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                    max_samples=param_max_samples[best_value_IsoForest],
                                    contamination=0.01,
                                    max_features=param_max_features[best_value_IsoForest],
                                    bootstrap=param_bootstrap[best_value_IsoForest],
                                    random_state=101).fit(X)).decision_function(X)
        #here we use the decision function=> the decision function provides us a value, which represents the models confidence
        ##that the data point is an outlier
        if len(df_feat_outl[df_feat_outl['{}_{}_IsoFor'.format(match,sent)]<0]) > (len(df_feat_outl['{}_{}_IsoFor'.format(match,sent)])*0.1):
            df_feat_outl['{}_{}_IsoFor'.format(match,sent)]=(IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                        max_samples=param_max_samples[best_value_IsoForest],
                                        contamination=0.01,
                                        max_features=param_max_features[best_value_IsoForest],
                                        bootstrap=param_bootstrap[best_value_IsoForest],
                                        random_state=101).fit(X)).decision_function(X)*-1
            df_feat_outl['{}_{}_IsoFor_Rank'.format(match,sent)]=df_feat_outl['{}_{}_IsoFor'.format(match,sent)].rank()
            outliers_df = df_feat_outl[df_feat_outl['{}_{}_IsoFor'.format(match, sent)] < 0].reset_index()
            
            IsoPred_Vis=IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                max_samples=param_max_samples[best_value_IsoForest],
                                contamination=0.01,
                                max_features=param_max_features[best_value_IsoForest],
                                bootstrap=param_bootstrap[best_value_IsoForest],
                                random_state=101).fit_predict(X)
            
            outlier_index=np.where(IsoPred_Vis==-1)
            outlier_values=X[outlier_index]
            
            if not outliers_df.empty:
                display(outliers_df[['Date_Month','Wrestler']])
            else:
                print('No outliers found.')


            sns.scatterplot(x=X[:,0], y=X[:,1])
            sns.scatterplot(x=outlier_values[:,0], y=outlier_values[:,1], color='r')
            plt.ylabel(sent)
            plt.xlabel(match)
            plt.title('Outlier Detection Isolation Forest {} - {}'.format(match,sent))
            plt.show()
        else:
            df_feat_outl['{}_{}_IsoFor_Rank'.format(match,sent)]=df_feat_outl['{}_{}_IsoFor'.format(match,sent)].rank()
            outliers_df = df_feat_outl[df_feat_outl['{}_{}_IsoFor'.format(match, sent)] < 0].reset_index()
            
            IsoPred_Vis=IsolationForest(n_estimators=param_n_estimator[best_value_IsoForest],
                                max_samples=param_max_samples[best_value_IsoForest],
                                contamination=0.01,
                                max_features=param_max_features[best_value_IsoForest],
                                bootstrap=param_bootstrap[best_value_IsoForest],
                                random_state=101).fit_predict(X)
            
            outlier_index=np.where(IsoPred_Vis==-1)
            outlier_values=X[outlier_index]
            
            if not outliers_df.empty:
                display(outliers_df[['Date_Month','Wrestler']])
            else:
                print('No outliers found.')


            sns.scatterplot(x=X[:,0], y=X[:,1])
            sns.scatterplot(x=outlier_values[:,0], y=outlier_values[:,1], color='r')
            plt.ylabel(sent)
            plt.xlabel(match)
            plt.title('Outlier Detection Isolation Forest {} - {}'.format(match,sent))
            plt.show()