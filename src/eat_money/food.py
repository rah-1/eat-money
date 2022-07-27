class Food:
    # this is a very basic class, there can be more nutrition variables if needed (investigate API!)
    # future consideration: add setters too
    def __init__(self, date, name, cost, calories, carbs, protein, fat, sugar, sodium):
        self._date = date
        self._name = name
        self._cost = cost
        self._calories = calories
        self._carbs = carbs
        self._protein = protein
        self._fat = fat
        self._sugar = sugar
        self._sodium = sodium

    def get_date(self):
        return self._date

    def get_name(self):
        return self._name

    def get_cost(self):
        return self._cost

    def get_calories(self):
        return self._calories

    def get_carbs(self):
        return self._carbs

    def get_protein(self):
        return self._protein

    def get_fat(self):
        return self._fat

    def get_sugar(self):
        return self._sugar

    def get_sodium(self):
        return self._sodium

    def set_cost(self, cost):
        self._cost = cost

    name = property(get_name)
    cost = property(get_cost, set_cost)
    calories = property(get_calories)
    carbs = property(get_carbs)
    protein = property(get_protein)
    fat = property(get_fat)
    sugar = property(get_sugar)
    sodium = property(get_sodium)
