import requests
import pandas as pd
import datetime as dt
import time

"""
CALL ADVICE, HOW TO, AND MISC FOR A UNIQUE LIST YEARLY
"""

myurl = 'https://api.nytimes.com/svc/books/v3/lists.json?list=advice-how-to-and-miscellaneous&published-date='

#set first date in 2013
pub_date = dt.datetime(2013,4,28)
api_key = 'bf8slfiurDryZVoCT75NazIy0qpSLkti'

#create empty booklist dataframe
booklist = pd.DataFrame(columns=['Date', 'Title', 'Author', 'ISBN13', 'ISBN13_2', 'ISBN13_3', 'Description', 'GoogleCategory'])

#call API for book lists before 2014
while pub_date < dt.datetime(2014,1,1):
    
    # update the query url with the pub_date
    query = myurl + pub_date.strftime('%Y-%m-%d') + '&api-key=' + api_key
    
    # call API
    response = requests.get(query)
    data = response.json()
    
    # Add the list of 10 books to the dataframe
    for i in range (len(data['results'])):
        # If the current book is not already in the list, add it to the dataframe
        check = str(data['results'][i]['isbns'][0]['isbn13']) in booklist['ISBN13'].tolist()
        if check == False:
            
            #if there is more than 2 ISBN, store the first 3
            if len(data['results'][i]['isbns']) >2: 
                booklist= booklist.append(pd.DataFrame({'Date':pub_date,'Title':data['results'][i]['book_details'][0]['title'], 'Author':data['results'][i]['book_details'][0]['author'], 'ISBN13':data['results'][i]['isbns'][0]['isbn13'],'ISBN13_2':data['results'][i]['isbns'][1]['isbn13'],'ISBN13_3':data['results'][i]['isbns'][2]['isbn13']},index=[0]), ignore_index=True)
            #if there are 2 ISBNs, store 2
            elif len(data['results'][i]['isbns'])==2: 
                booklist= booklist.append(pd.DataFrame({'Date':pub_date,'Title':data['results'][i]['book_details'][0]['title'], 'Author':data['results'][i]['book_details'][0]['author'], 'ISBN13':data['results'][i]['isbns'][0]['isbn13'],'ISBN13_2':data['results'][i]['isbns'][1]['isbn13']},index=[0]), ignore_index=True)
            # else, store 1
            else: 
                booklist= booklist.append(pd.DataFrame({'Date':pub_date,'Title':data['results'][i]['book_details'][0]['title'], 'Author':data['results'][i]['book_details'][0]['author'], 'ISBN13':data['results'][i]['isbns'][0]['isbn13']},index=[0]), ignore_index=True)
          
    # Add a week to the pub date before re-calling the API
    pub_date += dt.timedelta(days=7)
    
    time.sleep(7)
    
"""
PULL DESCRIPTION FROM GOOGLE API
"""
#set initial API URL
googleURL='https://www.googleapis.com/books/v1/volumes?q=isbn:'

# loop through all books in combined booklist
for j in range(len(booklist.index)):
    # call google API with 1st ISBN
    ISBN=booklist.iloc[j,4]
    query2 = googleURL + ISBN
    response2 = requests.get(query2)
    description = response2.json()
    time.sleep(1)
    
    # if the first ISBN doesn't work, try second
    if description['totalItems']==0:
        ISBN=booklist.iloc[j,5]
        query2 = googleURL + ISBN
        response2 = requests.get(query2)
        description = response2.json()
        time.sleep(1)
        
        # if second ISBN doesn't work, try 3rd
        if description['totalItems']==0:
            ISBN=booklist.iloc[j,6]
            query2 = googleURL + ISBN
            response2 = requests.get(query2)
            description = response2.json()
            time.sleep(1)
            
            #if 3rd ISBN doesn't work, skip this book
            if description['totalItems']==0: continue
            # if it does work- add description & category to df
            booklist.iloc[j,2]=description['items'][0]['volumeInfo']['description']
            # add google category
            booklist.iloc[j,3]=description['items'][0]['volumeInfo']['categories'][0]
        
        # if second ISBN works, add to df
        else:
            # add description
            booklist.iloc[j,2]=description['items'][0]['volumeInfo']['description']
            # add google category
            booklist.iloc[j,3]=description['items'][0]['volumeInfo']['categories'][0]
    # if first ISBN works, add to df
    else:
        # add description
        booklist.iloc[j,2]=description['items'][0]['volumeInfo']['description']
        # add google category
        booklist.iloc[j,3]=description['items'][0]['volumeInfo']['categories'][0]
