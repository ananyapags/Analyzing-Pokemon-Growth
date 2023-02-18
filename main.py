"""Pokemon Analysis 
Using statistics and a minimum of three plots -> looking to see which type of Pokemon trains the fastest, and which type is the strongest

Every species of Pokemon has:
* a growth rate 
* base stats
* base experience 

API Resource: https://pokeapi.co/

Additional Resources:
* Base Stats: https://bulbapedia.bulbagarden.net/wiki/Base_stats
* Growth Rate and Experience: https://bulbapedia.bulbagarden.net/wiki/
* Pokedex: https://pokedex.org/
* Growth rates : https://pokeapi.co/docs/v2#growth-rates

Analysis:

1. Countplot of growth rates for each type
2. Boxplot comparing the average base stats amongst types
3. Barplot comparing base experience levels amongst types

I love coding

"""

import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns

typeList = ['poison', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'grass', 'fighting', 'psychic', 'steel', 'ice', 'rock', 'dragon', 'dark', 'ghost']
typeListAbv = ['p','f','fl','w','b','n','e','g','fa','gr','fi','p','s','i','r','d','dar','gh']

# create and empty DataFrame
PokeDF = pd.DataFrame(columns = ["Species","Type","Base Experience","Growth",
                                 "Health","Attack","Defense","Special-Attack",
                                 "Special-Defense","Speed"])
id = 1
while True:
  # create a new empty row 
  row = {"Species":"","Type":"","Base Experience":"","Growth":"","Health":"",
         "Attack":"","Defense":"","Special-Attack":"","Special-Defense":"",
         "Speed":""}

  #make the request
  url='https://pokeapi.co/api/v2/pokemon/' + str(id) + '/'
  r = requests.get(url)
  if r.status_code != 200:
    break # break once we get an error code (we've gotten all the possible pokemon)
  data = r.json()

  # fill the row ans append to the DataFrame
  row["Species"] = data['name']
  row["Type"] = data['types'][0]["type"]["name"] # only record the first type for simplicity
  row["Base Experience"] = data["base_experience"]
  row["Health"] = data['stats'][0]['base_stat']
  row["Attack"] = data['stats'][1]['base_stat']
  row["Defense"] = data['stats'][2]['base_stat']
  row["Special-Attack"] = data['stats'][3]['base_stat']
  row["Special-Defense"] = data['stats'][4]['base_stat']
  row["Speed"] = data['stats'][5]['base_stat']
  PokeDF = PokeDF.append(row, ignore_index = True)
  id += 1

display(PokeDF)
print("TOTAL # OF POKEMON:", len(PokeDF))

# flip the DataFrame so that the indexes are the names of the Pokemon
PokeDF = PokeDF.set_index("Species")
display(PokeDF)

# investigate the 6 different possibilities for growth rates
url = 'https://pokeapi.co/api/v2/growth-rate/'
r = requests.get(url)
data = r.json()
for x in data["results"]:
  print(x)

# get the growth rates
PokeDF["Growth Formula"] = [0 for i in range(len(PokeDF))] # new empty column
for i in range(1,7):
  url = 'https://pokeapi.co/api/v2/growth-rate/'+str(i)+'/' # For each growth rate
  r = requests.get(url)
  data = r.json()
  for j in range(len(data['pokemon_species'])): # loop through all pokemon that have this growth rate
    key = data["pokemon_species"][j]["name"] # save the name of the pokemon 
    for name in PokeDF.index:
      if key in name: 
        # check that the "name" contains the "key" since they're not always exactly equal (due to inconsistencies in the API )
        # (ex. the "thundrus" key is actually "thundurus-incarnate" in the PokeDF.index)
        PokeDF.loc[name,'Growth'] = data["name"]
        PokeDF.loc[name, 'Growth Formula'] = data['formula'] 

display(PokeDF)

"""<h3>Growth Rate Formulas</h3>

Here are functionz used to calucate the growth rate needed for the analysis

Slow: $\frac{5x^3}{4}$

Medium Slow: $\frac{6x^3}{5} - 15x^2 + 100x - 140$

Medium (Medium Fast): $x^3$

Fast: $\frac{4x^3}{5}$

Fast then Very Slow(Fluctuating): $\begin{cases}
\frac{ x^3 \left( 24 + \left\lfloor \frac{x+1}{3} \right\rfloor \right) }{50},  & \text{if } x \leq 15  \\
\frac{ x^3 \left( 14 + x \right) }{50},     & \text{if } 15 < x \leq 35  \\
\frac{ x^3 \left( 32 + \left\lfloor \frac{x}{2} \right\rfloor \right ) }{50},   & \text{if } x > 35  \\
\end{cases}$

Slow then Very Fast (Erratic): $\begin{cases}
\frac{ x^3 \left( 100 - x \right) }{50},    & \text{if } x \leq 50  \\
\frac{ x^3 \left( 150 - x \right) }{100},   & \text{if } 50 < x \leq 68  \\
\frac{ x^3 \left( 1274 + (x \bmod 3)^2 - 9 (x \bmod 3) - 20 \left\lfloor \frac{x}{3} \right\rfloor \right) }{1000}, & \text{if } 68 < x \leq 98  \\
\frac{ x^3 \left( 160 - x \right) }{100},   & \text{if } x > 98  \\
\end{cases}$

"""

plt.figure().set_size_inches(5, 15)
sns.countplot(data=PokeDF, y="Type", hue="Growth").set(title="Growth Rates for Each Type")
plt.show()
print()


# instead of dvanced graphs in matplotlib, seaborn lineplot showing the different rates
x = np.arange(0,100,5)
plt.plot(x,x**3,'r--',x,((6*x**3)/5)-(15*x**2)+(100*x)-(140),'bs',x, (5*x**3)/3,'g^', x, (4/5)*x**3, "co")
plt.title("Comparison of Different Growth Rates")
plt.savefig("plot.png")
plt.ylabel("EXP Points Needed to Level Up")
plt.xlabel("Level")
plt.show()
plt.clf()

print("\nLEGEND:")
print("Green = Slow")
print("Blue = Medium Slow")
print("Red = Medium Fast")
print("Cyan = Fast")
print()

"""Conclusion: Medium Fast is the most common growth rate across the board. Bug, Fairy, and Ghost have some of the fastest growth rates, while Dragon, Psychic, and Steel have some of the slowest. """

stats = ["Health","Attack","Defense","Special-Attack","Special-Defense","Speed"]
total = [0 for i in range(len(PokeDF))]
for stat in stats:
  total += PokeDF[stat]
total /= len(stats)
PokeDF["Average Base Stats"] = total

plt.figure().set_size_inches(7,5)
sns.boxplot(data=PokeDF, x="Average Base Stats", y="Type")
plt.savefig('boxplot.png')
plt.show()

"""Dragon, Psychic, and Steel have the highest average base stats. However, they are also some of the slowest to train."""

typebase = {}
typecount = {}
for j in range(1,len(PokeDF)+1): # Total Pokemon
  url='https://pokeapi.co/api/v2/pokemon/' + str(j) + '/'
  r= requests.get(url)
  data = r.json()
  base=int(data['base_experience'])
  typeName = data['types'][0]['type']['name']

  if typeName in typebase:
    typebase[typeName] += base
  elif typeName not in typebase:
    typebase[typeName] = base


for j in range(1,len(typeList)): 
  url='https://pokeapi.co/api/v2/type/' + str(j) + '/'
  r= requests.get(url)
  data = r.json()
  count = len(data['pokemon'])
  typeName = data['name']
  typecount[typeName]=count

print(typebase) # total base experience for each type
print(typecount) # total number of pokemon each type

typebase = {'grass': 10864, 'fire': 8293, 'water': 15737, 'bug': 8951, 'normal': 14579, 'poison': 4421, 'electric': 6021, 'ground': 4393, 'fairy': 2593, 'fighting': 3923, 'psychic': 8904, 'rock': 6521, 'ghost': 3778, 'ice': 3425, 'dragon': 5211, 'dark': 4175, 'steel': 4337, 'flying': 497}
typecount = {'normal': 130, 'fighting': 78, 'flying': 135, 'poison': 85, 'ground': 82, 'rock': 89, 'bug': 96, 'ghost': 73, 'steel': 77, 'fire': 88, 'water': 162, 'grass': 124, 'electric': 89, 'psychic': 123, 'ice': 58, 'dragon': 78, 'dark': 76, 'fairy': 72}

finaldict=typebase
for i in typecount:
  finaldict[i]/=typecount[i]
  
types = []
basevalue = []
for i in finaldict:
  types.append(i)
  basevalue.append(int(finaldict[i]))

plt.xticks(rotation=90)
sns.barplot(x=typeList,y=basevalue)
plt.savefig('scatter.png')
plt.show()
plt.clf()

"""Conclusion: Normal, Water, and Fire have the highest base experience. 
Flying, Fairy, and Fighting have the lowest base experience.


Bug, Fairy, and Ghost have some of the fastest growth rates, while Dragon, Psychic, and Steel have some of the slowest. We used a countplot to visualize the different growth rates for each type. It could be helpful to determine the percentage of each growth rate for each type as well. Bug seems to be the fastest to train. 

Dragon, Psychic, and Steel have the highest average base stats. Normal, Water, and Fire have the highest base experience. Flying, Fairy, and Fighting have the lowest base experience. The base stats matter more than the highest base experience because they will ultimately determine the upper limit of power. High base experience just starts you with more power initially. The strongest type is likely Dragon.
"""