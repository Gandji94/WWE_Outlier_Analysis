# Outlier Analysis for WWE Wrestler

For this project I created a YouTube Comment Scrapper, which allowed me to collect YouTube comments from the videos of the YouTube channel Wrestlelamia.

Link: https://www.youtube.com/@Wrestlelamia

These comments were cleaned, aggregated, added a sentiment algorithm (Vader library) and combined with match data from the profightdb website.

Link: http://www.profightdb.com/

This data was used to perform an outlier analysis, where we analysed the combination of positive comments and matches lost by the wrestler. This decision was made because we could not find enough wrestlers with more negative than positive comments.
The decision to analyse wrestlers' losses and positive comments was made to see if the wrestlers were being booked well or badly. For example, if a wrestler has a lot of positive comments, he should not have a lot of losses. But we also expect to find positive outliers, wrestlers with the most positive comments and few losses.

The following algorithms were used to find the outliers:

- Isolation Forest
- One-Class SVM

The project is broken down in five different jupyter notebooks

1. Scrapping_WWE_YouTube_Comments
2. Setting_up_the_Data_Transformation_Code
3. Creating_Final_DataFrames_WWE
4. WWE_Comments_Exploratory_Analysis
5. WWE_Comments_Outlier_Detection

Every bigger code sample is in a python file, which will allow people to use the code for themselves.