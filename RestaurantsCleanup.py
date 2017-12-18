# Import libraries
import pandas as pd

# Bring in restaurants.csv
rest = pd.read_csv('restaurants.csv')

g = rest['distance'].groupby(rest['name']).describe()
g.reset_index(inplace=True)
g['distance'] = g['min']
g = g[['name','distance']]

reduced = pd.merge(rest,g,left_on=['name','distance'],right_on=['name','distance'])

h = reduced['neighborhood'].groupby(reduced['name']).describe()
h.reset_index(inplace=True)
h['neighborhood']=h['top']
h = h[['name','neighborhood']]

final_list = pd.merge(reduced,h,left_on=['name','neighborhood'],right_on=['name','neighborhood'])


# Write to restaurants.csv
final_list.to_csv('restaurants_final.csv',encoding='utf-8')
