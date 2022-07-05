from datetime import date
from food import Food
from CalorieNinja import find_food_data
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.core.window import Window
import csv

Config.set('graphics', 'resizable', True)

class MyApp(App):
    def build(self):
        # window title
        self.title = "Eat Money"
        self._light_theme = True
        
        #window color
        Window.clearcolor = (1,1,1,1)
        # these store the current name/cost based on user entry
        self._curr_name = ""
        self._curr_cost = ""

        # units of time available
        # in the future, want the ability to "remember" preferences
        self._units = ["Daily", "Weekly", "Monthly", "Annual"]
        self._curr_unit = self._units[0]

        # reads in old data from csv upon build start
        # stores Food objects in food_list
        self._food_list = []
        self.read_old_data()

        # boolean variable to switch between food and cost entry
        # its basically an easy way to track which entry field is
        # being used at the moment
        self._first_click = False

        self._today = date.today()
        # print("Today's date:", self._today.strftime("%B %d, %Y"))

        # layout convention: grid
        # this means that each of the widgets (labels, buttons, etc.)
        # will each fit somewhere in the "grid" (makes things easier to orient)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # todo: logo widget
        # self.window.add_widget(Image(source="logo_filename.png"))
        
        #add logo
        self.window.add_widget(Image(source='eatmoneylogo.png'))
        #return Image(source = 'eatmoneylogo.png')

        # label widget for the header
        # labels are the kivy name for text-only widgets
        # also, color scheme/theme can be changed... preferences?
        self.header = Label(
            text="eat money",
            font_size=95,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.header)
        
        self.date = Label(
            text=self._today.strftime("%B %d, %Y"),
            font_size=45,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.date)

        # text input widget for user input
        self.input_field = TextInput(
            multiline=False,
            size_hint=(1, 0.5)
        )
        self.window.add_widget(self.input_field)

        # button widget to submit text entry
        self.submit_button = Button(
            text="SUBMIT FOOD",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#C19ADD',
        )
        self.submit_button.bind(on_release=self.big_button_press)
        self.window.add_widget(self.submit_button)

        # button widget to access stats (implementation currently tentative)
        self.stats_button = Button(
            text="VIEW STATS",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#C19ADD',
        )
        self.stats_button.bind(on_release=self.view_stats_button)
        self.window.add_widget(self.stats_button)

        self.theme_button = Button(
            text="CHANGE THEME",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#C19ADD',
        )
        self.theme_button.bind(on_release=self.change_theme_button)
        self.window.add_widget(self.theme_button)

        # label widget to display important info
        # ex. if user input is invalid/successful
        self.infobox = Label(
            text="welcome to eat money!",
            font_size=35,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.infobox)

        return self.window

    # this is a function to read in the csv file to load old data
    # it turns the csv rows into Food objects and stores them in food_list
    def read_old_data(self):
        with open("data.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    date = row[0]
                    name = row[1]
                    cost = row[2]
                    calories = row[3]

                    food_item = Food(date, name, cost, calories)
                    self._food_list.append(food_item)

                line_count += 1

    # this function is for when we want to write new data
    # it is invoked when we submit food/cost info
    def add_new_data(self, data):
        with open('data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    # input validation for cost field entry
    # checks whether a valid float was entered
    def check_valid_cost(self, entry):
        try:
            cost = float(entry)
            return True
        except ValueError:
            self.infobox.text = "Please enter a valid cost!"
            return False

    # this function corresponds to the behavior when we click
    # the topmost button (its name will change upon selection,
    # so I've decided to call it "big button")

    # additionally, this should also ideally be where the API call
    # to get nutrient data happens. between submitting food and cost,
    # we need to devise a mechanism to lookup the user-entered food
    # in whatever nutrition database we're using and keep track of that
    # data (this will likely involve adding more attributes to the Food class
    # and/or this class)
    # TODO: API things (see above) --> goal is to have this in the prototype
    def big_button_press(self, instance):
        # the if-else corresponds to which button is currently "up"
        # this first (if) block runs when we are at the submit cost menu
        # the second (else) block runs when we are at the submit food menu
        if self._first_click:
            if self.check_valid_cost(self.input_field.text):
                self.submit_button.text = "SUBMIT FOOD"
                self._curr_cost = self.input_field.text
                self._first_click = False

                # add Food object
                calories = find_food_data(self._curr_name)
                curr_food = Food(self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, calories)
                data_entry = [self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, calories]
                self.infobox.text = self._curr_name + " ($" + self._curr_cost + ") added successfully!"
                self._food_list.append(curr_food)
                self.add_new_data(data_entry)

        else:
            if self.input_field.text == "":
                self.infobox.text = "Please enter a valid name!"
            else:
                self.submit_button.text = "SUBMIT COST ($)"
                self._curr_name = self.input_field.text
                self.infobox.text = "Please enter the cost of " + self._curr_name
                self._first_click = True
        self.input_field.text = ""


    def calc_stats(self):
        # variables to return -- may need more later
        total_cost = 0
        total_calories = 0
       
        if self._curr_unit == self._units[0]:
            date_comparison_value = self._today.day
            str_selection_start = 0
            str_selection_end = 2
        elif self._curr_unit == self._units[1]:
            date_comparison_value = self._today.isocalendar().week
            str_selection_start = 0
            str_selection_end = 2
        elif self._curr_unit == self._units[2]:
            date_comparison_value = self._today.month
            str_selection_start = 3
            str_selection_end = 5
        if self._curr_unit == self._units[3]:
            date_comparison_value = self._today.year
            str_selection_start = 6
            str_selection_end = 10

        for food in reversed(self._food_list):
            # todo: deal with weird weekly behavior later
            if self._curr_unit == self._units[1]:
                pass
            else:
                if int(food.get_date()[str_selection_start:str_selection_end]) == int(date_comparison_value):
                    total_cost += float(food.get_cost())
                    total_calories += float(food.get_calories())
                else:
                    break

        return total_cost, total_calories


    # todo: when stats button is pressed (popup?)
    # there is a way to get popup windows.
    # personally, I think keeping the landing page/menu
    # simple is the way to go -- the popup window would have
    # all the important stats (spending, nutrition, history, etc.)
    # alternatively, we would overwrite the same page and not have
    # to deal with popup windows (not that it's hard, this is an
    # aesthetic choice). what do you think will be best?
    def view_stats_button(self, instance):
        cost_output, calories_output = self.calc_stats()

        popup_layout = GridLayout(cols=1)
        popup_spending_header = Label(
            text=self._curr_unit + " Spending:",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_spending = Label(
            text="$" + "{:.2f}".format(cost_output),
            font_size=36,
            color='#FFFFFF',
            halign='center'
        )
        popup_nutrition_header = Label(
            text=self._curr_unit + " Nutrition:",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_nutrition = Label(
            text="{:.2f}".format(calories_output) + " cals",
            font_size=36,
            color='#FFFFFF',
            halign='center'
        )

        popup_layout.add_widget(popup_spending_header)
        popup_layout.add_widget(popup_spending)
        popup_layout.add_widget(popup_nutrition_header)
        popup_layout.add_widget(popup_nutrition)

        popup = Popup(title='User Statistics',
                      content=popup_layout,
                      size_hint=(None, None), size=(400, 400))

        popup.open()

    def change_theme_button(self, instance):
        if self._light_theme:
            Window.clearcolor = (0,0,0,0)
            self._light_theme = False
        else:
            Window.clearcolor = (1,1,1,1)
            self._light_theme = True


if __name__ == '__main__':
    MyApp().run()
