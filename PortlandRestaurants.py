# Import libraries
import requests
import pandas as pd

###################
#### FUNCTIONS ####
###################
# Define function to bring in Yelp API credentials (Get your own!)
def getCred(line):
    with open('credentials.txt') as f:
        credentials = [x.strip().split(':') for x in f.readlines()]
        
    return credentials[line][0]
  
# Define function to retreive data via API connection
def yelpCall(neighborhood,limit):

    app_id = getCred(0)
    app_secret = getCred(1)
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
      
    resp = requests.get(url=url, params=params, headers=headers)
    
    return resp.json()['businesses']

# Define function to get best restaurants in each neighborhood
def neighborhoodReviews(neighborhood,limit):

    rd = pd.DataFrame.from_dict(yelpCall(neighborhood,limit))
    
    # Category
    rd['category'] = rd.categories.apply(lambda x: x[0]['title'])
    # Latitude
    rd['latitude'] = rd.coordinates.apply(lambda x: x['latitude'])
    # Longitude
    rd['longitude'] = rd.coordinates.apply(lambda x: x['longitude'])
    # Street Address
    rd['address'] = rd.location.apply(lambda x: x['display_address'][0])
    # Neighborhood
    rd['neighborhood'] = neighborhood
    
    return rd[columns]

###################
#### PROCESSING STEPS ####
###################

# Definte desired results
columns = ['neighborhood','name','distance','category','address','display_phone' \
           ,'price','rating','review_count','url','latitude','longitude']
final = pd.DataFrame(columns=columns)

# Bring in neighborhoods
nhoods = pd.read_csv('neighborhoods.csv')

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
    
# Clean out duplicate restaurants
clean = final.sort_values('distance', ascending=True).groupby(['name']).head(1)

# Write to restaurants.csv
clean.to_csv('restaurants.csv',encoding='utf-8')



