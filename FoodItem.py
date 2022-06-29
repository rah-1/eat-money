class FoodItem:
    # this is a very basic class, there can be more nutrition variables if needed (investigate API!)
    # future consideration: add setters too
    def __init__(self, date, name, cost, calories):
        self._date = date
        self._name = name
        self._cost = cost
        self._calories = calories

    def get_date(self):
        return self._date

    def get_name(self):
        return self._name

    def get_cost(self):
        return self._cost

    def get_calories(self):
        return self._calories

    name = property(get_name)
    cost = property(get_cost)
    calories = property(get_calories)
