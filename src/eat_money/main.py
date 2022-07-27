

from datetime import date
import os

from kivymd.uix.toolbar import MDToolbar, MDBottomAppBar

from eat_money.food import Food
from eat_money.CalorieNinja import find_food_data

#TODO: will need to add kivymd in project requirements/packaging
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.label import Label
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp


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
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.app import runTouchApp


import json
import csv

Config.set('graphics', 'resizable', True)

input_helper = """
MDTextField:
    hint_text: "Enter info"
    multiline: False
"""

class MyApp(MDApp):
    def build(self):
        Window.bind(on_keyboard=self.dismiss_popup_key_press)

        # window title
        self.title = "Eat Money"
        self._light_theme = True

        # window color
        Window.clearcolor = (1, 1, 1, 1)
        # these store the current name/cost based on user entry
        self._curr_name = ""
        self._curr_cost = ""

        # units of time available
        # in the future, want the ability to "remember" preferences
        self._units = ["Daily", "Weekly", "Monthly", "Annual"]
        self._curr_unit = self._units[0]

        # reads in old data from csv upon build start
        # stores Food objects in food_list
        self._daily_spent = 0.00
        self._daily_cals = 0.0
        self._food_list = []
        self.read_old_data()
        self.calc_old_data_daily()

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
        self.window.size_hint = (0.5, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # add logo
        self.window.add_widget(Image(source='eatmoneylogo.png'))

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
            font_size=20,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.date)

        # todo: reformat daily fields and pad decimals

        # add daily spent label
        self.spent_disp = Label(
            text="Daily Spending: ".ljust(30) + "$" + "{0:06.2f}".format(round(self._daily_spent, 2)),
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.spent_disp)

        # add daily calories label
        self.cal_disp = Label(
            text="Daily Calories: ".ljust(30) + str(round(self._daily_cals,1)) + " cals",
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.cal_disp)


        # text input widget for user input
        self.input_field = Builder.load_string(input_helper)
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

        # button widget to view history (implementation also tentative)
        self.history_button = Button(
            text="VIEW HISTORY",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#C19ADD',
        )
        self.history_button.bind(on_release=self.view_history_button)
        self.window.add_widget(self.history_button)

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

        self.remember_preference()

        self.input_field.bind(on_text_validate=lambda x:self.big_button_press("idk"))

        return self.window

    # this function dismisses any open popup windows
    # if the user presses ESC, SPACE, or ENTER
    # side-note: kivy closes the main window when ESC is pressed normally
    def dismiss_popup_key_press(self, key, scancode, codepoint, modifiers, idk):
        if isinstance(App.get_running_app().root_window.children[0], Popup):
            if scancode == 13 or scancode == 27 or scancode == 32:
                App.get_running_app().root_window.children[0].dismiss()


    def remember_preference(self):
        with open('preferences.json', 'r') as r_prefs:
            prefs_dict = json.load(r_prefs)

        # currently hardcoded for num of preferences (2)
        if len(prefs_dict) == 2:
            if prefs_dict["theme"] == "dark":
                self.change_theme_button("new")
            if prefs_dict["unit"].title() in self._units:
                self._curr_unit = prefs_dict["unit"].title()

    def save_preferences(self):
        if self._light_theme:
            prefs_dict = {"theme": "light", "unit": self._curr_unit.lower()}
        else:
            prefs_dict = {"theme": "dark", "unit": self._curr_unit.lower()}
        with open('preferences.json', 'w') as w_prefs:
            json.dump(prefs_dict, w_prefs, indent=4)

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
                    carbs = row[4]
                    protein = row[5]
                    fat = row[6]
                    sugar = row[7]
                    sodium = row[8]

                    food_item = Food(date, name, cost, calories, carbs, protein, fat, sugar, sodium)
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
            self.infobox.text = "please enter a valid cost!"
            return False

    def calc_old_data_daily(self):
        for food in reversed(self._food_list):
            if int(food.get_date()[8:10]) == int(date.today().day):
                self._daily_spent += float(food.get_cost())
                self._daily_cals += float(food.get_calories())

    # todo: ensure this displays the same way as initial disp
    def update_daily_disp(self):
        self.cal_disp.text = "Daily Calories: ".ljust(30) + str(round(self._daily_cals,1)) + " cals"
        self.spent_disp.text = "Daily Spending: ".ljust(30) + "$" + "{0:06.2f}".format(round(self._daily_spent, 2))

    def md_helper(self, idk):
        self.input_field.focus = True

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
                # add Food object
                food_list = find_food_data(self._curr_name, self._today.strftime("%Y-%m-%d"), self._curr_cost)
                menu_text = ""
                # check if list is empty
                if len(food_list) == 0:
                    self.infobox.text = "unable to locate " + self._curr_name + " in database!"
                else:
                    for item in food_list:
                        data_entry = [self._today.strftime("%Y-%m-%d"), item.get_name(), self._curr_cost,
                                      item.get_calories(), item.get_carbs(), item.get_protein(), item.get_fat(),
                                      item.get_sugar(), item.get_sodium()]
                        self.add_new_data(data_entry)
                        self._food_list.append(item)
                        self._daily_cals += float(item.get_calories())
                        self._daily_spent += float(item.get_cost())
                        menu_text += (item.get_name() + ", ")
                    menu_text = menu_text[0:len(menu_text)-2]
                    self.infobox.text = menu_text + " ($" + self._curr_cost + ") added successfully!"

        else:
            if self.input_field.text == "":
                self.infobox.text = "please enter a valid name!"
            else:
                self.submit_button.text = "SUBMIT COST ($)"
                self._curr_name = self.input_field.text
                self.infobox.text = "please enter the cost of " + self._curr_name
                self._first_click = True
        self.input_field.text = ""
        self.update_daily_disp()
        Clock.schedule_once(self.md_helper)

    # since we don't yet officially have a "reset" button,
    # this function seeks to emulate that behavior; it will be
    # called when the other menu buttons are pressed
    def reset_user_entry(self):
        self.submit_button.text = "SUBMIT FOOD"
        self._first_click = False
        self._curr_name = ""
        self._curr_cost = ""
        self.input_field.text = ""
        self.infobox.text = "welcome to eat money!"

    def calc_stats(self):
        # variables to return -- may need more later
        total_cost = 0
        total_calories = 0
        total_carbs = 0
        total_protein = 0
        total_fat = 0
        total_sugar = 0
        total_sodium = 0


        if self._curr_unit == self._units[0]:
            date_comparison_value = self._today.day
            str_selection_start = 8
            str_selection_end = 10
        elif self._curr_unit == self._units[1]:
            date_comparison_value = self._today.isocalendar().week
            str_selection_start = 8
            str_selection_end = 10
        elif self._curr_unit == self._units[2]:
            date_comparison_value = self._today.month
            str_selection_start = 5
            str_selection_end = 7
        if self._curr_unit == self._units[3]:
            date_comparison_value = self._today.year
            str_selection_start = 0
            str_selection_end = 4

        for food in reversed(self._food_list):
            if self._curr_unit == self._units[1]:
                if int(date(int(food.get_date()[0:4]), int(food.get_date()[5:7]), int(food.get_date()[8:10])).isocalendar().week) == int(date_comparison_value):
                    total_cost += float(food.get_cost())
                    total_calories += float(food.get_calories())
                    total_carbs += float(food.get_carbs())
                    total_protein += float(food.get_protein())
                    total_fat += float(food.get_fat())
                    total_sugar += float(food.get_sugar())
                    total_sodium += float(food.get_sodium())
            else:
                if int(food.get_date()[str_selection_start:str_selection_end]) == int(date_comparison_value):
                    total_cost += float(food.get_cost())
                    total_calories += float(food.get_calories())
                    total_carbs += float(food.get_carbs())
                    total_protein += float(food.get_protein())
                    total_fat += float(food.get_fat())
                    total_sugar += float(food.get_sugar())
                    total_sodium += float(food.get_sodium())
                else:
                    break

        return total_cost, total_calories, total_carbs, total_protein, total_fat, total_sugar, total_sodium

    def view_stats_button(self, instance):
        if instance == "new":
            self._stats_popup.dismiss()
        self.reset_user_entry()
        cost_output, calories_output, carbs_output, protein_output, fat_output, sugar_output, sodium_output = self.calc_stats()

        popup_layout = GridLayout(cols=1)
        popup_unit_button = Button(
            text="CHANGE UNIT",
            size_hint=(1, 0.8),
            bold=True,
            background_color='#C19ADD',
        )
        popup_unit_button.bind(on_release=self.rotate_units)
        popup_spending_header = Label(
            text=self._curr_unit + " Spending:",
            underline=True,
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_spending = Label(
            bold=True,
            text="$" + "{:.2f}".format(cost_output),
            font_size=36,
            color='#FFFFFF',
            halign='center'
        )
        popup_nutrition_header = Label(
            text=self._curr_unit + " Nutrition:",
            underline=True,
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_calories = Label(
            bold=True,
            text="{:.1f}".format(calories_output) + " cals",
            font_size=36,
            color='#FFFFFF',
            halign='center'
        )
        popup_carbs = Label(
            text="{:.1f}".format(carbs_output) + "g of carbs",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_protein = Label(
            text="{:.1f}".format(protein_output) + "g of protein",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_fat = Label(
            text="{:.1f}".format(fat_output) + " g of total fats",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_sugar = Label(
            text="{:.1f}".format(sugar_output) + " g of sugar",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_sodium = Label(
            text="{:.1f}".format(sodium_output) + " g of sodium",
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )

        popup_layout.add_widget(popup_unit_button)
        popup_layout.add_widget(popup_spending_header)
        popup_layout.add_widget(popup_spending)
        popup_layout.add_widget(popup_nutrition_header)
        popup_layout.add_widget(popup_calories)
        popup_layout.add_widget(popup_carbs)
        popup_layout.add_widget(popup_protein)
        popup_layout.add_widget(popup_fat)
        popup_layout.add_widget(popup_sugar)
        popup_layout.add_widget(popup_sodium)

        self._stats_popup = Popup(title='User Statistics',
                                  content=popup_layout,
                                  size_hint=(None, None), size=(400, 550))

        self._stats_popup.open()

    def rotate_units(self, instance):
        curr_pos = self._units.index(self._curr_unit)
        if curr_pos != len(self._units) - 1:
            self._curr_unit = self._units[curr_pos + 1]
        else:
            self._curr_unit = self._units[0]

        self.save_preferences()
        self.view_stats_button("new")

    def history_helper(self, entry):
        popup_header = Label(
            text=entry,
            size_hint_y=None,
            font_size=24,
            color='#FFFFFF',
            halign='left'
        )
        return popup_header

    # view history by date:
    def view_history_button(self, instance):
        self.reset_user_entry()

        scroll = ScrollView(size_hint=(1, None), size=(700, 570))
        # retrieves item information from food list. adds each item as its own text widget
        history_list = []
        for item in self._food_list:
            history_list.append((item.get_date(), item.get_name(), item.get_calories(), "$%s" % item.get_cost(),
                                 item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(),
                                 item.get_sodium()))

        table = MDDataTable(column_data=[
            ("Date", dp(20)),
            ("Food", dp(25)),
            ("Calories", dp(20)),
            ("Cost", dp(15)),
            ("Carbs", dp(20)),
            ("Protein", dp(20)),
            ("Fat", dp(20)),
            ("Sugar", dp(20)),
            ("Sodium", dp(20))
        ],
            row_data=history_list
        )
        scroll.add_widget(table)
        # makes the widgets scrollable
        popup = Popup(title='History',
                      content=scroll,
                      size_hint=(None, None), size=(950, 700))
        popup.open()

    def change_theme_button(self, instance):
        self.reset_user_entry()
        if self._light_theme:
            #Window.clearcolor = (0, 0, 0, 0)
            if instance != "new":
                self.infobox.text = "applied dark theme!"
            self.theme_cls.theme_style = "Dark"
            self._light_theme = False
        else:
            #Window.clearcolor = (1, 1, 1, 1)
            self._light_theme = True
            self.infobox.text = "applied light theme!"
            self.theme_cls.theme_style = "Light"
        self.save_preferences()


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    MyApp().run()


if __name__ == '__main__':
    main()
