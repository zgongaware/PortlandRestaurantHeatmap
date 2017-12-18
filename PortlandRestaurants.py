# Import libraries
import requests
import pandas as pd

# Definte desired results
columns = ['neighborhood','name','distance','category','address','display_phone' \
           ,'price','rating','review_count','url','latitude','longitude']
final = pd.DataFrame(columns=columns)

# Bring in neighborhoods
nhoods = pd.read_csv('neighborhoods.csv')

# Bring in Yelp API credentials (Get your own!)
with open('credentials.txt') as f:
  credentials = [x.strip().split(':') for x in f.readlines()]
  

# Define function to get best restaurants in each neighborhood
def neighborhoodReviews(neighborhood,limit):
    # API connection
    app_id = credentials[0][0]
    app_secret = credentials[1][0]
    data = {'grant_type': 'client_credentials',
            'client_id': app_id,
            'client_secret': app_secret}
    token = requests.post('https://api.yelp.com/oauth2/token', data=data)
    access_token = token.json()['access_token']
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' % access_token}
    params = {'location': neighborhood + ',Portland, OR',
              'term': 'Restaurant',
              'sort_by': 'distance',
              'limit': limit,
             }
      
    # Save the response
    resp = requests.get(url=url, params=params, headers=headers)
      
    rd = pd.DataFrame.from_dict(resp.json()['businesses'])
    
    # Category
    category = []
    for index,row in rd.iterrows():
        category.insert(index,rd.categories[index][0]['title'])
    rd['category'] = category
    
    # Latitude
    lat = []
    for index,row in rd.iterrows():
        lat.insert(index,rd.coordinates[index]['latitude'])
    rd['latitude'] = lat
    
    # Longitude
    lon = []
    for index,row in rd.iterrows():
        lon.insert(index,rd.coordinates[index]['longitude'])
    rd['longitude'] = lon
    
    # Address
    addr = []
    # Need to add checks for third address rows here
    for index,row in rd.iterrows():
        addr.insert(index,rd.location[index]['display_address'][0]) #\
               # + ' ' + rd.location[index]['display_address'][1])
    rd['address'] = addr
    
    rd['neighborhood'] = neighborhood
    
    return rd[columns]
    #final.append([final,rd[columns]],ignore_index=True)

# Set a limit for the loop, just in case
limit = 125
iteration = 0

# Find best restaurants in each neighborhood
for index,row in nhoods.iterrows():
    result = neighborhoodReviews(nhoods.iloc[index]['Names'],50)
    final = pd.concat([final,result],ignore_index=True)
    iteration += 1
    if iteration == limit:
        break

# Write to restaurants.csv
final.to_csv('restaurants.csv',encoding='utf-8')

