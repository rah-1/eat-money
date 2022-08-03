from datetime import date
import os

from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.toolbar import MDToolbar, MDBottomAppBar

from eat_money.food import Food
from eat_money.CalorieNinja import find_food_data
from eat_money.text_helper import input_helper, date_helper, food_helper, cost_helper, list_helper

#TODO: will need to add kivymd in project requirements/packaging
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import Label
from kivymd.uix.list import MDList, TwoLineAvatarListItem
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp


from kivy.app import App
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
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
import sqlite3

Config.set('graphics', 'resizable', True)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class MyApp(MDApp):
    theme_color = get_color_from_hex('#8CA262')
    def build(self):
        Window.bind(on_keyboard=self.dismiss_popup_key_press)
        self._selection_list = []
        self.date = None
        self.cost = None
        self.food = None
        self._item_selected = False
        self._selected_index = None
        self.index_press = None
        self.selected_obj = None

        # window title
        self.title = "Eat Money"
        self._light_theme = True

        # window color
        Window.clearcolor = (1, 1, 1, 1)
        win_x, win_y = Window.size
        Window.minimum_width = win_x
        Window.minimum_height = win_y

        # these store the current name/cost based on user entry
        self._curr_name = ""
        self._curr_cost = ""

        # units of time available
        self._units = ["Daily", "Weekly", "Monthly", "Annual"]
        self._curr_unit = self._units[0]

        # default assignment for BMR values
        self._age = 25
        self._heightcm = 180
        self._weightkg = 75
        self._sex = "m"

        # reads in old data from csv upon build start
        # stores Food objects in food_list
        self._daily_spent = 0.00
        self._daily_cals = 0
        self._food_list = []
        self._sqlite_connection = sqlite3.connect("data.db")
        self._sqlite_cursor = self._sqlite_connection.cursor()
        self._sqlite_commands = []
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
        self.window = GridLayout(spacing="1dp")
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
            halign='center',
            font_name='comic'
        )
        self.window.add_widget(self.header)

        self.date = Label(
            text=self._today.strftime("\n%B %d, %Y"),
            font_size=20,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.date)

        # add daily spent label
        self.spent_disp = Label(
            text= "$" + "{0:00.2f}".format(round(self._daily_spent, 2)) + " spent today",
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.spent_disp)

        #add daily calories label
        self.cal_disp = Label(
            text=str(round(self._daily_cals,1)) + " cals consumed today",
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.cal_disp)

        # text input widget for user input
        self.input_field = Builder.load_string("""MDTextField:
            hint_text: "Enter info"
            multiline: False""")
        self.input_field.focus = True
        self.window.add_widget(self.input_field)

        # button widget to submit text entry
        self.submit_button = MDRaisedButton(
            text="SUBMIT FOOD",
            size_hint=(1, 0.5),
            md_bg_color=(67/255,53/255,76/255,1),
            _no_ripple_effect=True
        )
        self.submit_button.bind(on_release=self.big_button_press)
        self.window.add_widget(self.submit_button)

        # button widget to access stats (implementation currently tentative)
        self.stats_button = MDRaisedButton(
            text="VIEW STATS",
            size_hint=(1, 0.5),
            md_bg_color=(67/255,53/255,76/255,1),
            _no_ripple_effect=True
        )
        self.stats_button.bind(on_release=self.view_stats_button)
        self.window.add_widget(self.stats_button)

        # button widget to view history (implementation also tentative)
        self.history_button = MDRaisedButton(
            text="VIEW HISTORY",
            size_hint=(1, 0.5),
            md_bg_color=(67/255,53/255,76/255,1),
            _no_ripple_effect=True
        )
        self.history_button.bind(on_release=self.view_history_button)
        self.window.add_widget(self.history_button)


        # button widget for recommended caloric intake
        self.rec_button = MDRaisedButton(
            text="CALORIC EXPENDITURE",
            size_hint=(1, 0.5),
            md_bg_color=(67 / 255, 53 / 255, 76 / 255, 1),
            _no_ripple_effect=True
        )
        self.rec_button.bind(on_release=self.view_rec_button)
        self.window.add_widget(self.rec_button)

        self.theme_button = MDRaisedButton(
            text="CHANGE THEME",
            size_hint=(1, 0.5),
            md_bg_color=(67/255,53/255,76/255,1),
            _no_ripple_effect=True
        )
        self.theme_button.bind(on_release=self.change_theme_button)
        self.window.add_widget(self.theme_button)

        # label widget to display important info
        # ex. if user input is invalid/successful
        self.infobox = Label(
            text="welcome to eat money!",
            font_size=35,
            color='#8CA262',
            halign='center',
            font_name='comic'
        )
        self.window.add_widget(self.infobox)

        self.remember_preference()

        self.input_field.bind(on_text_validate=lambda x: self.big_button_press("idk"))

        self.create_datatable()

        return self.window

    # this function dismisses any open popup windows
    # if the user presses ESC, SPACE, or ENTER
    # side-note: kivy closes the main window when ESC is pressed normally
    def dismiss_popup_key_press(self, key, scancode, codepoint, modifiers, idk):
        if isinstance(App.get_running_app().root_window.children[0], Popup):
            if scancode == 27:
                App.get_running_app().root_window.children[0].dismiss()


    def remember_preference(self):
        with open('preferences.json', 'r') as r_prefs:
            prefs_dict = json.load(r_prefs)

        # currently hardcoded for num of preferences (2)
        if len(prefs_dict) == 6:
            if prefs_dict["theme"] == "dark":
                self.change_theme_button("new")
            if prefs_dict["unit"] in self._units:
                self._curr_unit = prefs_dict["unit"]
            if self.check_valid_cost(prefs_dict["age"], False):
                self._age = prefs_dict["age"]
            if self.check_valid_cost(prefs_dict["height"], False):
                self._heightcm = prefs_dict["height"]
            if self.check_valid_cost(prefs_dict["weight"], False):
                self._weightkg = prefs_dict["weight"]
            if prefs_dict["sex"] == "f":
                self._sex = "f"

    def save_preferences(self):
        if self._light_theme:
            prefs_dict = {"theme": "light", "unit": self._curr_unit.lower(),
                          "age": self._age, "height": self._heightcm,
                          "weight": self._weightkg, "sex": self._sex}
        else:
            prefs_dict = {"theme": "dark", "unit": self._curr_unit.lower(),
                          "age": self._age, "height": self._heightcm,
                          "weight": self._weightkg, "sex": self._sex}
        with open('preferences.json', 'w') as w_prefs:
            json.dump(prefs_dict, w_prefs, indent=4)

    # this is a function to read in the csv file to load old data
    # it turns the sql rows into Food objects and stores them in food_list
    def read_old_data(self):
        self._sqlite_cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_nutrition_data (
                    date text,
                    name text,
                    cost real,
                    calories real,
                    carbs real,
                    protein real,
                    fat real,
                    sugar real,
                    sodium real
                    );""")
        self._sqlite_cursor.execute("SELECT * FROM user_nutrition_data ORDER BY date")
        results = self._sqlite_cursor.fetchall()
        if len(results) > 0:
            for row in results:
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

    # this function is for when we want to write new data
    # it is invoked when we submit food/cost info
    def add_new_data(self, data):
        sql_command_string = "INSERT INTO user_nutrition_data VALUES ("
        for i in range(len(data)):
            if (type(data[i]) is str):
                sql_command_string += "'" + data[i] + "'"
            else:
                sql_command_string += str(data[i])
            if i != len(data) - 1:
                sql_command_string += ", "
        sql_command_string += ")"
        self._sqlite_commands.append(sql_command_string)

    # input validation for cost field entry
    # checks whether a valid float was entered
    def check_valid_cost(self, entry, usage):
        try:
            cost = float(entry)
            return True
        except ValueError:
            if usage:
                self.infobox.text = "please enter a valid cost!"
            return False

    def calc_old_data_daily(self):
        self._daily_spent = 0
        self._daily_cals = 0
        for food in reversed(self._food_list):
            if int(food.get_date()[8:10]) == int(date.today().day) and int(food.get_date()[5:7]) == int(date.today().month) and int(food.get_date()[0:4]) == int(date.today().year):
                self._daily_spent += float(food.get_cost())
                self._daily_cals += float(food.get_calories())

    def update_daily_disp(self):
        self.spent_disp.text = "$" + "{0:00.2f}".format(round(self._daily_spent, 2)) + " spent today"
        self.cal_disp.text = str(round(self._daily_cals,1)) + " cals consumed today"

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
            if self.check_valid_cost(self.input_field.text, True):
                self.submit_button.text = "SUBMIT FOOD"
                self._curr_cost = self.input_field.text
                self._first_click = False

                # add Food object
                food_list = find_food_data(self._curr_name, self._today.strftime("%Y-%m-%d"), self._curr_cost)
                menu_text = ""
                # check if list is empty
                if len(food_list) == 0:
                    self.infobox.text = "unable to locate " + self._curr_name + " in database!"
                else:
                    for item in food_list:
                        item.cost = round(float(self._curr_cost) / len(food_list), 2)
                        data_entry = [self._today.strftime("%Y-%m-%d"), item.get_name(), item.get_cost(),
                                      item.get_calories(), item.get_carbs(), item.get_protein(), item.get_fat(),
                                      item.get_sugar(), item.get_sodium()]

                        self.add_new_data(data_entry)
                        self._food_list.append(item)
                        self._daily_cals += float(item.get_calories())
                        self._daily_spent += float(item.get_cost())
                        menu_text += (item.get_name() + ", ")
                    menu_text = menu_text[0:len(menu_text) - 2]
                    self.infobox.text = menu_text + " ($" + self._curr_cost + ") added successfully!"
                    self.update_daily_disp()
                    self.create_datatable()

        else:
            if self.input_field.text == "":
                self.infobox.text = "please enter a valid name!"
            else:
                self.submit_button.text = "SUBMIT COST ($)"
                self._curr_name = self.input_field.text
                self.infobox.text = "please enter the cost of " + self._curr_name
                self._first_click = True
        self.input_field.text = ""
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
                    break
            elif self._curr_unit == self._units[0] or self._curr_unit == self._units[2]:
                if int(food.get_date()[str_selection_start:str_selection_end]) == int(date_comparison_value)\
                        and int(food.get_date()[5:7])==int(self._today.month) and int(food.get_date()[0:4])==\
                        int(self._today.year):
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

        self._stats_popup = Popup(title='User Statistics (ESC to close)',
                                  content=popup_layout,
                                  size_hint=(None, None), size=(400, 550))

        self._stats_popup.open()

    def view_rec_button(self, instance):
        if instance == "new":
            self._rec_popup.dismiss()
        self.reset_user_entry()

        bmr = self.bmr(self._age, self._heightcm, self._weightkg, self._sex)

        popup_layout_new = GridLayout(cols=1, spacing = '1dp')

        popup_total_header = Label(
            text="Resting Caloric Expenditure:",
            underline=True,
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_total = Label(
            bold=True,
            text="{:.1f}".format(bmr) + " cals",
            font_size=40,
            color='#FFFFFF',
            halign='center'
        )
        popup_remaining_header = Label(
            text="Calories Remaining:",
            underline=True,
            font_size=24,
            color='#FFFFFF',
            halign='center'
        )
        popup_remaining = Label(
            bold=True,
            text="{:.1f}".format(bmr - self._daily_cals) + " cals",
            font_size=40,
            color='#FFFFFF',
            halign='center'
        )
        self.age_input_field = Builder.load_string("""MDTextField:
            write_tab: False
            current_hint_text_color: [1,1,1,0.6]
            line_color_normal: [1,1,1,0.15]
            hint_text: "Enter age"
            multiline: False""")
        self.ht_input_field = Builder.load_string("""MDTextField:
            write_tab: False
            current_hint_text_color: [1,1,1,0.6]
            line_color_normal: [1,1,1,0.15]
            hint_text: "Enter height (cm)"
            multiline: False""")
        self.wt_input_field = Builder.load_string("""MDTextField:
            write_tab: False
            current_hint_text_color: [1,1,1,0.6]
            line_color_normal: [1,1,1,0.15]
            hint_text: "Enter weight (kg)"
            multiline: False""")
        self.sex_input_field = Builder.load_string("""MDTextField:
            write_tab: False
            current_hint_text_color: [1,1,1,0.6]
            line_color_normal: [1,1,1,0.15]
            hint_text: "Enter sex (m/f)"
            multiline: False""")

        self.age_input_field.bind(on_text_validate=lambda x: self.rec_tb_transfer(0))
        self.ht_input_field.bind(on_text_validate=lambda x: self.rec_tb_transfer(1))
        self.wt_input_field.bind(on_text_validate=lambda x: self.rec_tb_transfer(2))
        self.sex_input_field.bind(on_text_validate=lambda x: self.update_user_info("idk"))

        self.popup_rec_status = Label(
            text="View and update basal metabolic rate (BMR) data",
            font_size=16,
            color='#FFFFFF',
            halign='center'
        )

        if instance == "new":
            self.popup_rec_status.text = "Updated user information successfully!"

        popup_update_button = MDRaisedButton(
            text="UPDATE USER INFO",
            size_hint=(1, 0.8),
            md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1)
        )
        popup_close_button = MDRaisedButton(
            text="Close",
            size_hint=(1, 0.8),
            md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1)
        )
        popup_update_button.bind(on_release=self.update_user_info)

        popup_layout_new.add_widget(popup_total_header)
        popup_layout_new.add_widget(popup_total)
        popup_layout_new.add_widget(popup_remaining_header)
        popup_layout_new.add_widget(popup_remaining)
        popup_layout_new.add_widget(self.age_input_field)
        popup_layout_new.add_widget(self.ht_input_field)
        popup_layout_new.add_widget(self.wt_input_field)
        popup_layout_new.add_widget(self.sex_input_field)
        popup_layout_new.add_widget(self.popup_rec_status)
        popup_layout_new.add_widget(popup_update_button)
        popup_layout_new.add_widget(popup_close_button)


        self._rec_popup = Popup(title='Caloric Expenditure (ESC to close)',
                                  content=popup_layout_new,
                                  size_hint=(None, None), size=(500, 550))
        popup_close_button.bind(on_release=self._rec_popup.dismiss)

        self._rec_popup.open()

    def rec_tb_transfer(self, id):
        if id == 0:
            self.age_input_field.focus = False
            self.ht_input_field.focus = True
        if id == 1:
            self.ht_input_field.focus = False
            self.wt_input_field.focus = True
        if id == 2:
            self.wt_input_field.focus = False
            self.sex_input_field.focus = True

    def update_user_info(self, idk):
        move_forward = True
        if not self.check_valid_cost(self.age_input_field.text, False):
            move_forward = False
            self.age_input_field.text = ""
        if not self.check_valid_cost(self.ht_input_field.text, False):
            move_forward = False
            self.ht_input_field.text = ""
        if not self.check_valid_cost(self.wt_input_field.text, False):
            move_forward = False
            self.wt_input_field.text = ""
        if self.sex_input_field.text.lower() != 'm' and self.sex_input_field.text.lower() != 'f':
            move_forward = False
            self.sex_input_field.text = ""

        if not move_forward:
            self.popup_rec_status.text = "Please enter valid user information!"
        else:
            self._age = float(self.age_input_field.text)
            self._heightcm = float(self.ht_input_field.text)
            self._weightkg = float(self.wt_input_field.text)
            self._sex = self.sex_input_field.text.lower()
            self.save_preferences()
            self.view_rec_button("new")

    def rotate_units(self, instance):
        curr_pos = self._units.index(self._curr_unit)
        if curr_pos != len(self._units) - 1:
            self._curr_unit = self._units[curr_pos + 1]
        else:
            self._curr_unit = self._units[0]

        self.save_preferences()
        self.view_stats_button("new")

    def on_button_press(self, instance_button: MDRaisedButton) -> None:
        #print("success button press")
        '''Called when a control button is clicked.'''

        try:
            {
                "EDIT ENTRIES": self.edit_row,
                "DELETE ENTRY": self.remove_row,
                "MODIFY ENTRY": self.change_row,
            }[instance_button.text]()
        except KeyError:
            pass

    def item_press(self, num):
        self.index_press = num

    def set_index(self):
        if(self._item_selected):
            self._selected_index = self.index_press

    def unselect_item(self, instance):
        self.selected_obj.do_unselected_item()
        self.change_popup.dismiss()

    def on_selected(self, instance_selection_list, instance_selection_item):
        if len(self._food_list) == 0:
            instance_selection_item.do_unselected_item()
        if len(instance_selection_list.get_selected_list_items()) > 1:
            instance_selection_item.do_unselected_item()
        if len(instance_selection_list.get_selected_list_items()) == 1 and not self._item_selected:
            self._item_selected = True
            self.selected_obj = instance_selection_item
            self.set_index()
        if len(instance_selection_list.get_selected_list_items()) == 0:
            self._item_selected = False

    def on_unselected(self, instance_selection_list, instance_selection_item):
        if len(instance_selection_list.get_selected_list_items()) == 0:
            self._item_selected = False
            # self._selection_list = instance_selection_list.get_selected_list_items()

    def edit_row(self) -> None:
        #print("success edit row")

        layout = GridLayout(rows=4,spacing="1dp")
        # button_layout = GridLayout(rows=2,spacing="1dp",size_hint=(1,None),size=(650,90))
        scroll = ScrollView(size_hint=(1,1), size=(650,230))
        history_layout = Builder.load_string(list_helper)
        c = None
        bg = None
        index = 1
        # retrieves item information from food list. adds each item as its own text widget
        if self._light_theme:
            c = (0, 0, 0, 1)
            bg = "#FFFFFF"
        else:
            c = (1, 1, 1, 1)
            bg = '#212121'
        if (len(self._food_list) > 0):
            for item in reversed( self._food_list):
                # icon = IconLeftWidget(icon="blank")
                food_header = TwoLineAvatarListItem(
                    theme_text_color='Custom',
                    bg_color = bg,
                    text_color = c,
                    secondary_theme_text_color = 'Custom',
                    secondary_text_color = c,
                    text=item.get_name() + " ($" + str(item.get_cost()) + ")",
                    on_press=lambda x, smth = index: self.item_press(smth),
                    secondary_text=item.get_date(),
                    _no_ripple_effect=True,
                )
                # food_header.add_widget(icon)
                history_layout.add_widget(food_header)
                index+=1
                # print(food_header)
        else:
            no_entry = TwoLineAvatarListItem(
                #TODO: need to test this functionality
                text="No entries to date!",
                theme_text_color='Custom',
                text_color= c,
                bg_color=bg
            )
            history_layout.add_widget(no_entry)

        # makes the widgets scrollable
        scroll.add_widget(history_layout)
        layout.add_widget(scroll)
        for button_text in ["DELETE ENTRY", "MODIFY ENTRY"]:
            layout.add_widget(
                MDRaisedButton(
                    text=button_text, on_release=self.on_button_press,size_hint=(1,None),size=(650,90),
                    md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1)
                )
            )
        close_button = MDRaisedButton(text="Close", md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1), size_hint=(1,None),size=(650,90))
        # layout.add_widget(button_layout)
        layout.add_widget(close_button)

        self.edit_popup = Popup(title='Edit Entries (Hold Row to Select, Drag and Move to Scroll)',
                                title_color=( 0, 0, 0, 1),
                                content=layout,
                                background='',
                                size_hint=(None, None), size=(650, 500))
        close_button.bind(on_press=self.close_edit_button)
        self.edit_popup.open()
        self.history_popup.dismiss()

    def close_edit_button(self, instance):
        # self.history_popup.dismiss()
        # self.view_history_button(None)
        self.create_datatable()
        self.history_popup.open()
        self.edit_popup.dismiss()

    def remove_item(self, num):
        #storing data that identifies a particular food entry for deletion in the sql database
        identifying_data = [self._food_list[num].get_date(), self._food_list[num].get_name(), self._food_list[num].get_cost()]
        del self._food_list[num]
        self.calc_old_data_daily()
        self.update_daily_disp()
        return identifying_data

    def remove_row(self) -> None:
        #print("success remove row")
        if self._item_selected:
            size = len(self._food_list)
            num = size - self._selected_index

            #passes identifying attributes into queue_update_db so that the correct tuple can be deleted
            identifying_data = self.remove_item(num)
            self.queue_delete_from_db(identifying_data)
            # self.create_datatable()
            self._item_selected = False

    def change_row(self) -> None:
        #print("CHANGE ROW SUCCESS")

        if self._item_selected:
            size = len(self._food_list)
            item = self._food_list[size-self._selected_index]
            layout = GridLayout(rows=5)
            buttons = GridLayout(cols=2)

            self.date = Builder.load_string(date_helper)
            self.food = Builder.load_string(food_helper)
            self.cost = Builder.load_string(cost_helper)

            self.date.text = item.get_date()
            self.food.text = item.get_name()
            self.cost.text = str(item.get_cost())

            close_button = MDRectangleFlatButton(text="Close",
                                                 theme_text_color="Custom",
                                                 text_color=(193 / 255, 154 / 255, 221 / 255, 1),
                                                 line_color=(193 / 255, 154 / 255, 221 / 255, 1))
            submit_button = MDFlatButton(text="Save",
                                         theme_text_color="Custom",
                                         text_color=(193 / 255, 154 / 255, 221 / 255, 1),
                                         line_color=(193 / 255, 154 / 255, 221 / 255, 1),
                                         on_release=self.check_entry)

            buttons.add_widget(submit_button)
            buttons.add_widget(close_button)

            layout.add_widget(self.date)
            layout.add_widget(self.food)
            layout.add_widget(self.cost)
            layout.add_widget(buttons)

            self.change_status = Label(
                text="Change entry details",
                font_size=16,
                color='#000000',
                halign='center'
            )
            layout.add_widget(self.change_status)
            self.change_popup = Popup(title='Modify Entry',
                                      background='',
                                      title_color=(0, 0, 0, 1),
                                      content=layout,
                                      size_hint=(None, None), size=(350, 300))
            close_button.bind(on_press=self.unselect_item)
            self.change_popup.open()

    def check_entry(self, instance):
        # print("UPDATE ENTRY")
        size = len(self._food_list)
        num = size - self._selected_index
        item = self._food_list[num]
        move_foward = True
        food_list = []

        # print(type(self.food.text))

        self.food.text = self.food.text.strip()
        self.date.text = self.date.text.strip()
        self.cost.text = self.cost.text.strip()
        self.change_status.text = 'Please enter valid information!'
        # print(self.food.text)
        if self.date.text == "":
            self.date.text = item.get_date()
            move_foward = False
        elif self.cost.text == "":
            self.cost.text = item.get_cost()
            move_foward = False
        elif self.food.text == "":
            self.food.text = item.get_name()
            move_foward=False
        elif self.cost.text == str(item.get_cost()).strip() and self.date.text == item.get_date().strip() and self.food.text == item.get_name().strip():
            self.change_status.text = "No New Information Entered!"
            move_foward = False
        elif not self.check_valid_cost(self.cost.text,False):
            move_foward = False
            self.cost.text=item.get_cost()
        elif not self.check_date(self.date.text):
            move_foward = False
            self.date.text=item.get_date()
        else:
            if self.food.text == item.get_name():
                #("SAME ITEM")
                food = Food(self.date.text, item.get_name(), self.cost.text, item.get_calories(),
                              item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(),
                              item.get_sodium())
                food_list.append(food)
            else:
                food_list = find_food_data(self.food.text, self.date.text, self.cost.text)

                if len(food_list) == 0:
                    self.change_status.text = " Unable to locate " + self.food.text + " in database!"
                    move_foward = False
                elif len(food_list) > 1:
                    self.change_status.text = " Too many food items listed!"
                    move_foward = False

        #TODO: get rid of pressing space to exit pop-up

        if not move_foward:
            pass
            #print('nothing')
            # self.change_status.text = 'Please enter valid information!'

        else:
            identifying_data = self.remove_item(num)
            food = food_list[0]
            self._food_list.append(food)
            self._food_list.sort(key=lambda x: x.get_date())
            self.calc_old_data_daily()
            self.update_daily_disp()
            self.change_status.text = "Entry successfully changed!"
            # add data to data entry(csv)
            # add data to food_list
            self.queue_delete_from_db(identifying_data)
            data_entry = [food.get_date(), food.get_name(), food.get_cost(),
                          food.get_calories(), food.get_carbs(), food.get_protein(), food.get_fat(),
                          food.get_sugar(), food.get_sodium()]
            self.add_new_data(data_entry)
            # sort list
            #update item entry
            self.change_popup.dismiss()
            # self.history_popup.dismiss()
            # self.create_datatable()
            self._item_selected = False


        #check if entry statements are valid

    def check_date(self, date):
        for count, element in enumerate(date):
            if len(date) != 10:
                return False
            if (count >= 0 and count <= 3) or count == 5 or count == 6 or count == 8 or count == 9:
                # print(element)
                if not element.isdigit():
                    return False
                    # print(count + " ERROR" + element)
            if count == 4 or count == 7:
                # print(element)
                if element != "-":
                    # print(count + " ERROR" + element)
                    return False
        return True

    def queue_delete_from_db(self, identifying_data):
        lines = []
        
        sql_command_string = "DELETE FROM user_nutrition_data WHERE date='" + identifying_data[0] + "' AND name='" + identifying_data[1] + "' AND cost='" + str(identifying_data[2]) + "'"
        self._sqlite_commands.append(sql_command_string)

        self.edit_popup.dismiss()
        self.edit_row()

    # view history by date:

    def create_datatable(self):
        layout = GridLayout(rows=3, spacing="1dp")

        # retrieves item information from food list. adds each item as its own text widget
        history_list = []
        for num, item in enumerate(reversed(self._food_list)):
            history_list.append((
                                num + 1, item.get_date(), item.get_name(), item.get_calories(), "$%s" % item.get_cost(),
                                item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(),
                                item.get_sodium()))

        # this framework is limited and has bugs
        # datatables is weird: in order to click the check all without there being a bug, the number of rows must be displayed on the screen
        # TODO: change the rows_num=2 to a diff number (figure out how to format? for diff screens:
        self.data_tables = MDDataTable(size_hint=(1, 1),
                                       use_pagination=True,
                                       rows_num=5,
                                       column_data=[
                                           ("No.", dp(10)),
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
                                       row_data=history_list,
                                       )

        # add buttons to edit history
        layout.add_widget(self.data_tables)
        edit_button = MDRaisedButton(
            text="EDIT ENTRIES", on_release=self.on_button_press, size_hint=(1, None), size=(650, 90),
            md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1)
        )
        close_button = MDRaisedButton(text="Close", md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1),
                                      size_hint=(1, None), size=(650, 90))
        layout.add_widget(edit_button)
        layout.add_widget(close_button)
        self.history_popup = Popup(title='History (Drag and Move to Scroll)',
                                   content=layout,
                                   title_color=(0, 0, 0, 1),
                                   size_hint=(None, None), size=(650, 500),
                                   background=''
                                   )
        close_button.bind(on_press=self.history_popup.dismiss)

    def view_history_button(self, instance):
        self.reset_user_entry()
        self.history_popup.open()

    def change_theme_button(self, instance):
        self.reset_user_entry()
        self.md_helper("idk")
        if self._light_theme:
            Window.clearcolor = (0, 0, 0, 0)
            if instance != "new":
                self.infobox.text = "applied dark theme!"
            self.theme_cls.theme_style = "Dark"
            self._light_theme = False
        else:
            Window.clearcolor = (1, 1, 1, 1)
            self._light_theme = True
            self.infobox.text = "applied light theme!"
            self.theme_cls.theme_style = "Light"
        self.save_preferences()

    # calculates BMR (diff for m and f)
    def bmr(self, age, ht, wt, sex):
        if sex == "m":
            return 88.362 + (13.397 * wt) + (4.799 * ht) - (5.677 * age)
        elif sex == "f":
            return 447.593 + (9.247 * wt) + (3.098 * ht) - (4.330 * age)
        else:
            return 0


    def stop(self, *args):
        for statement in self._sqlite_commands:
            self._sqlite_cursor.execute(statement)
        self._sqlite_connection.commit()
        self._sqlite_connection.close()

def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    MyApp().run()

if __name__ == '__main__':
    main()
