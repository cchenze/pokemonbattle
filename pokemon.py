import requests
import random
import pandas as pd
import seaborn as sns ##novel component for data visualization (chart)
import matplotlib.pyplot as plt
from ipywidgets import interact_manual, interact
from IPython.display import display, HTML, Image
from ipyleaflet import Map, Marker ## novel component for data visualization (map)

def get_location_area():
    url = "https://pokeapi.co/api/v2/location-area/" ##novel component for pokemon api(1)
    query_string = {"offset" : 0, "limit" : 702}
    response = requests.get(url, params = query_string)
    response.raise_for_status()
    
    location_areas = response.json()
    location_area_list = []
    for location_area in location_areas['results']:
        location_area_list.append(location_area['name'])
    
    return location_area_list

def encounter_pokemon(location_area):
    url = f"https://pokeapi.co/api/v2/location-area/{location_area}" ##novel component for pokemon api(1)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    pokemon_name = data['pokemon_encounters'][0]["pokemon"]["name"]
    pokemon_min_level = data['pokemon_encounters'][0]["version_details"][0]["encounter_details"][0]["min_level"]
    pokemon_max_level = data['pokemon_encounters'][0]["version_details"][0]["encounter_details"][0]["max_level"]
    level = random.randint(pokemon_min_level, pokemon_max_level)
    
    return pokemon_name, level

def get_pokemon_stats(pokemon_name, level):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}" ##novel component for pokemon api(1)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    base_hp = data["stats"][0]['base_stat']
    base_attack = data["stats"][1]['base_stat']
    base_defense = data["stats"][2]['base_stat']
    base_speed = data["stats"][5]['base_stat']
    actual_hp = base_hp + level * 2
    actual_attack = base_attack + level
    actual_defense = base_defense + level
    actual_speed = base_speed + level

    data_for_dp = [[pokemon_name, "HP", actual_hp], 
                    [pokemon_name, "Attack", actual_attack], 
                    [pokemon_name, "Defense", actual_defense],
                    [pokemon_name, "Speed", actual_speed]]
    pokemon_stats = pd.DataFrame(data_for_dp, columns = ['Pokemon', 'parameter', 'value'])  
    return pokemon_stats, actual_hp, actual_attack, actual_defense, actual_speed

def get_pokemon_image(pokemon_name):
    url = f"https://pokeapi.glitch.me/v1/pokemon/{pokemon_name}" ##novel component for pokemon api(2)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    image_url = data[0]['sprite']
    
    return image_url

def generate_computer_pokemon():
    pokemon_id = random.randint(1,50)
    url = f"https://pokeapi.co/api/v2/evolution-chain/{pokemon_id}" ##novel component for pokemon api(1)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    return data['chain']['species']['name']

def evolve_to(pokemon_name):
    url = f"https://pokeapi.glitch.me/v1/pokemon/{pokemon_name}" ##novel component for pokemon api(2)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    return data[0]['family']['evolutionLine'][1]

def geocode(key,location):
    url = "http://www.mapquestapi.com/geocoding/v1/address" ##novel component for api from mapquestapi.com
    query_string = {"key" : key, "location" : location}
    response = requests.get(url, params = query_string)
    response.raise_for_status()
    data = response.json()
    
    return data['results'][0]['locations'][0]['latLng']['lat'], data['results'][0]['locations'][0]['latLng']['lng']

@interact_manual(location = get_location_area(), opponent = generate_computer_pokemon(), city = "")
def main(location, opponent, city):
    try:
        your_pokemon = encounter_pokemon(location)
        your_evolved_pokemon = evolve_to(your_pokemon[0])
        image = Image(url = get_pokemon_image(your_pokemon[0]), width=300, height=300)
        evolution_image = Image(url = get_pokemon_image(your_evolved_pokemon), width=300, height=300)
        stats = get_pokemon_stats(your_pokemon[0], your_pokemon[1])[0]

        opponent_level = your_pokemon[1]
        opponent_image = Image(url = get_pokemon_image(opponent), width=300, height=300)
        opponent_stats = get_pokemon_stats(opponent, your_pokemon[1])[0]

        comparison_frame = [stats, opponent_stats]
        result = pd.concat(comparison_frame) 

        ##output - user pokemon and image, computer pokemon and image
        display(HTML(f"<h3>Congratulations! You just captured a {your_pokemon[1]} level {your_pokemon[0]} in {location}!</h3>"))
        display(image)
        display(HTML(f"<h3>The opponent your pokemon is going to compete with is a {opponent_level} level {opponent}!</h3>"))
        display(opponent_image)

        sns.set_style('darkgrid')
        sns.set_context('paper')
        sns.barplot(x = "parameter", y = "value", hue = "Pokemon", data = result, palette = 'Blues')
        plt.title("Pokemon Comparison Stats for the Contest")

        your_pokemon_hp = get_pokemon_stats(your_pokemon[0], your_pokemon[1])[1]
        your_pokemon_attack = get_pokemon_stats(your_pokemon[0], your_pokemon[1])[2]
        your_pokemon_defense = get_pokemon_stats(your_pokemon[0], your_pokemon[1])[3]

        opponent_hp = get_pokemon_stats(opponent, your_pokemon[1])[1]
        opponent_attack = get_pokemon_stats(opponent, your_pokemon[1])[2]
        opponent_defense = get_pokemon_stats(opponent, your_pokemon[1])[3]

        ## output -- statements about match results and show the data visualization from dataframes
        if your_pokemon_attack <= opponent_defense and your_pokemon_defense >= opponent_attack:
            display(HTML(f"<h3>Which pokemon is going to win based on the data?</h3>"))
            plt.show()
            print("It is a tie!")
        elif (your_pokemon_attack > opponent_defense and your_pokemon_defense > opponent_attack) or (your_pokemon_attack > opponent_defense and your_pokemon_defense < opponent_attack and your_pokemon_hp / (opponent_attack - your_pokemon_defense) >= opponent_hp / (your_pokemon_attack - opponent_defense)):
            display(HTML(f"<h3>Which pokemon is going to win based on the data?</h3>"))
            plt.show()
            display(HTML("<h3>Congratulations! You won the match :)</h3>"))
            print(f"So your {your_pokemon[0]} evolved to the next stage {your_evolved_pokemon}!")
            display(evolution_image)
        else:
            display(HTML(f"<h3>Which pokemon is going to win based on the data?</h3>"))
            plt.show()
            print("Unfortunately, you lost the match :(")
            print(f"You have to release your {your_pokemon[0]} in your city to let it grow.")
            latlon = geocode("YOVMiEGw4Z90Koq8cw8EFqEBbh5HV00A", city)
            mymap = Map(center=latlon,zoom=13)
            marker = Marker(location=latlon, title=f"your pokemon: {your_pokemon[0]}")
            mymap.add_layer(marker)
            ##output -- display the map when user pokemon loses the match
            display(mymap)
    
    ##bad input handle
    except IndexError:
        print(f"Unable to find a pokemon in {location}. Please pick another location.")
    except NameError:
        print("Please run the program again to find a new opponent pokemon!")
    except HTTPError:
        print("Please run the program again to find a new opponent pokemon!")