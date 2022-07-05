import requests

#class goes into the CalorieNinja API to retrieve nutritional data about the food item then stores in in variables
#food parameter must be string
#returns the number of calories
def find_food_data(food):
    url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

    querystring = {"query":food}

    headers = {
        "X-RapidAPI-Key": "5f89cff6dfmshfce765dbd395312p13d19bjsn6baa74c01573",
        "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # response.json() returns a dict
    # response.text returns a string

    #break down json file to a dict with only the nutrition facts
    data = response.json()
    item_list = data['items']
    nutrition_list = item_list[0]

    #store nutrition information into variables
    #can maybe do stuff with the other info later
    sugar = nutrition_list['sugar_g']
    fiber = nutrition_list['fiber_g']
    sodium = nutrition_list['sodium_mg']
    name = nutrition_list['name']
    fat = nutrition_list['fat_total_g']
    calories = nutrition_list['calories']
    protein = nutrition_list['protein_g']
    carbs = nutrition_list['carbohydrates_total_g']
    
    return calories
    
    