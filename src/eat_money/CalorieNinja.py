import requests
from eat_money.food import Food

#class goes into the CalorieNinja API to retrieve nutritional data about the food item then stores in in variables
#food parameter must be string
#returns the number of calories
def find_food_data(food, date, cost):
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
    food_list = []
    # print(len(item_list))
    # if item_list == []:
    #     return -1, -1, -1, -1, -1, -1, -1
    if item_list == []:
        return food_list

    for item in item_list:
        # store nutrition information into variables
        # can maybe do stuff with the other info later
        sugar = item['sugar_g']
        sodium = item['sodium_mg']
        name = item['name']
        fat = item['fat_total_g']
        calories = item['calories']
        protein = item['protein_g']
        carbs = item['carbohydrates_total_g']

        food_item = Food(date, name, cost, calories, carbs, protein, fat, sugar, sodium)
        food_list.append(food_item)

        #TODO: need to fix the issue in that items 1,2,3 will all have the same cost when in reality ots the 3 items combined that is one cost


    return food_list