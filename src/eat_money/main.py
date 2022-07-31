from datetime import date
import os

from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.toolbar import MDToolbar, MDBottomAppBar

from eat_money.food import Food
from eat_money.CalorieNinja import find_food_data
from text_helper import input_helper, date_helper, food_helper, cost_helper, list_helper

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
from kivy.app import runTouchApp


import json
import csv

Config.set('graphics', 'resizable', True)

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
        self._daily_cals = 0
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
            font_size=85,
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

        #add daily calories label
        self.cal_disp = Label(
            text="Daily Calories: ".ljust(30) + "%s" % str(self._daily_cals),
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.cal_disp)

        #add daily spent label
        self.spent_disp = Label(
            text="Daily Spent: ".ljust(30) + "$%s" % str(self._daily_spent),
            font_size=25,
            size_hint=(1, 0.5),
            color='#8CA262',
            halign='left'
        )
        self.window.add_widget(self.spent_disp)

        # text input widget for user input
        self.input_field = Builder.load_string(input_helper)
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
            font_size=25,
            color='#8CA262',
            halign='center'
        )
        self.window.add_widget(self.infobox)

        self.remember_preference()

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
            if prefs_dict["unit"] in self._units:
                self._curr_unit = prefs_dict["unit"]

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
    def check_valid_cost(self, entry, usage):
        try:
            cost = float(entry)
            return True
        except ValueError:
            if usage:
                self.infobox.text = "please enter a valid cost!"
            return False

    def calc_old_data_daily(self):
        for food in reversed(self._food_list):
            if int(food.get_date()[8:10]) == int(date.today().day):
                self._daily_spent += float(food.get_cost())
                self._daily_cals += float(food.get_calories())

    def update_daily_disp(self):
        self.cal_disp.text = "Daily Calories: ".ljust(30) + "%s" % str(self._daily_cals)
        self.spent_disp.text = "Daily Spent:".ljust(30) + "$ %s" % str(self._daily_spent)
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
                #check if list is empty
                if len(food_list) == 0:
                    menu_text += "unable to locate " + self._curr_name + " in database!"
                else:
                    for item in food_list:
                        data_entry = [self._today.strftime("%Y-%m-%d"), item.get_name(), self._curr_cost, item.get_calories(), item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(), item.get_sodium()]
                        self.add_new_data(data_entry)
                        self._food_list.append(item)
                        self._daily_cals += float(item.get_calories())
                        self._daily_spent += float(item.get_cost())
                        menu_text += item.get_name() + " ($" + self._curr_cost + ") added successfully!" + "\n"
                self.infobox.text = menu_text
                #self.infobox.text = self._curr_name + " ($" + self._curr_cost + ") added successfully!"
                    # if calories != -1:
                    #     curr_food = Food(self._today.strftime("%Y-%m-%d"), db_name, self._curr_cost, calories, carbs, protein, fat, sugar, sodium)
                    #     data_entry = [self._today.strftime("%Y-%m-%d"), db_name, self._curr_cost, calories, carbs, protein, fat, sugar, sodium]
                    #     self.infobox.text = self._curr_name + " ($" + self._curr_cost + ") added successfully!"
                    #     self._food_list.append(curr_food)
                    #     self.add_new_data(data_entry)
                    # else:
                    #     self.infobox.text = "unable to locate " + self._curr_name + " in database!"
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

    def on_button_press(self, instance_button: MDRaisedButton) -> None:
        print("success button press")
        '''Called when a control button is clicked.'''

        try:
            {
                "EDIT ENTRIES": self.edit_row,
                "DELETE ENTRY": self.remove_row,
                "CHANGE ENTRY": self.change_row,
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
        print("success edit row")

        layout = GridLayout(rows=3, spacing="1dp")
        button_layout = GridLayout(cols=2,spacing="1dp",size_hint=(1,.105),size=(750,90))
        scroll = ScrollView()
        history_layout = Builder.load_string(list_helper)

        index = 1
        # retrieves item information from food list. adds each item as its own text widget
        if (len(self._food_list) > 0):
            for item in reversed( self._food_list):
                icon = IconLeftWidget(icon="checkbox-blank-circle")
                food_header = TwoLineAvatarListItem(
                    text=item.get_name() + " ($" + item.get_cost() + ")",
                    text_color=( 1, 1, 1, 0),
                    on_press=lambda x, smth = index: self.item_press(smth),
                    secondary_text=item.get_date(),
                    _no_ripple_effect=True,
                )
                food_header.add_widget(icon)
                history_layout.add_widget(food_header)
                index+=1
                # print(food_header)
        else:
            no_entry = TwoLineAvatarListItem(
                #TODO: need to test this functionality
                text="No entries to date!"
            )
            history_layout.add_widget(no_entry)

        # makes the widgets scrollable
        scroll.add_widget(history_layout)
        layout.add_widget(scroll)
        for button_text in ["DELETE ENTRY", "CHANGE ENTRY"]:
            button_layout.add_widget(
                MDRaisedButton(
                    text=button_text, on_release=self.on_button_press, size_hint=(1,None),size=(325,50),
                    md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1)
                )
            )
        close_button = MDRaisedButton(text="Close", md_bg_color=(193 / 255, 154 / 255, 221 / 255, 1), size_hint=(1,None),size=(750,90))
        layout.add_widget(button_layout)
        layout.add_widget(close_button)

        self.edit_popup = Popup(title='Edit Entries (Hold Row to Select)',
                                title_color=( 0, 0, 0, 1),
                                content=layout,
                                background='',
                                size_hint=(None, None), size=(650, 500))
        close_button.bind(on_press=self.edit_popup.dismiss)
        self.edit_popup.open()

    def remove_item(self, num):
        self._daily_spent -= float(self._food_list[num].get_cost())
        self._daily_cals -= float(self._food_list[num].get_calories())
        self.update_daily_disp()
        del self._food_list[num]

    def remove_row(self) -> None:
        print("success remove row")
        if self._item_selected:
            size = len(self._food_list)
            num = size - self._selected_index

            self.remove_item(num)
            self.update_csv(num)

            self._item_selected = False

    def change_row(self) -> None:
        print("CHANGE ROW SUCCESS")

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
            self.cost.text = item.get_cost()

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
            self.change_popup = Popup(title='Add Entry',
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
        elif self.cost.text == item.get_cost().strip() and self.date.text == item.get_date().strip() and self.food.text == item.get_name().strip():
            self.change_status.text = "No New Information Entered!"
            move_foward = False
        elif not self.check_valid_cost(self.cost.text,False):
            move_foward = False
            self.cost.text=item.get_cost()
        elif not self.check_date(self.date.text):
            move_foward = False
            self.date.text=item.get_date()
        elif not self.food.text.isalpha():
            move_foward = False
            self.food.text = item.get_name()
        else:
            if self.food.text == item.get_name():
                print("SAME ITEM")
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
            print('nothing')
            # self.change_status.text = 'Please enter valid information!'

        else:
            self.remove_item(num)
            food = food_list[0]
            self._food_list.append(food)
            self._food_list.sort(key=lambda x: x.get_date())
            self._daily_cals += float(item.get_calories())
            self._daily_spent += float(item.get_cost())
            self.update_daily_disp()
            self.change_status.text = "Entry successfully changed!"
            # add data to data entry(csv)
            # add data to food_list
            self.update_csv(num)
            # sort list
            #update item entry
            self.change_popup.dismiss()
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

    def update_csv(self, num):
        lines = []
        count = 0
        lines.append(['Date','Name','Cost','Calories','Carbs','Protein','Total Fats','Sugar','Sodium'])
        for item in self._food_list:
            data_entry = [item.get_date(), item.get_name(), item.get_cost(), item.get_calories(),
                          item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(), item.get_sodium()]
            lines.append(data_entry)

        with open('data.csv', 'w', newline='') as writeFile:
            # print("WRITE FILE")
            writer = csv.writer(writeFile)
            writer.writerows(lines)

        self.edit_popup.dismiss()
        self.history_popup.dismiss()
        obj = None
        self.view_history_button(obj)
        self.edit_row()

    # view history by date:
    def view_history_button(self, instance):
        self.reset_user_entry()
        layout = GridLayout(rows=3, spacing="1dp")

        # retrieves item information from food list. adds each item as its own text widget
        history_list = []
        for num, item in enumerate(reversed(self._food_list)):
            history_list.append((num+1, item.get_date(),item.get_name(),item.get_calories(),"$%s"%item.get_cost(), item.get_carbs(), item.get_protein(), item.get_fat(), item.get_sugar(), item.get_sodium()))

        # this framework is limited and has bugs
        # datatables is weird: in order to click the check all without there being a bug, the number of rows must be displayed on the screen
        #TODO: change the rows_num=2 to a diff number (figure out how to format? for diff screens:
        self.data_tables = MDDataTable(size_hint=(1, 1),
                                       use_pagination=True,
                                       rows_num=5,
                                       column_data=[
                                            ("No.", dp(20)),
                                            ("Date", dp(20)),
                                            ("Food", dp(25)),
                                            ("Calories", dp(20)),
                                            ("Cost", dp(15)),
                                            ("Carbs",dp(20)),
                                            ("Protein",dp(20)),
                                            ("Fat", dp(20)),
                                            ("Sugar", dp(20)),
                                            ("Sodium", dp(20))
                                        ],
                                        row_data = history_list,
                                        )

        #add buttons to edit history
        layout.add_widget(self.data_tables)
        edit_button = MDRaisedButton(
                    text="EDIT ENTRIES", on_release=self.on_button_press, size_hint=(1,None),size=(750,90),md_bg_color=(193/255,154/255,221/255,1)
                )
        close_button = MDRaisedButton(text="Close", md_bg_color=(193/255,154/255,221/255,1),size_hint=(1,None),size=(750,90))
        layout.add_widget(edit_button)
        layout.add_widget(close_button)
        self.history_popup = Popup(title='History',
                                   content=layout,
                                   title_color=(0, 0, 0, 1),
                                   size_hint=(None, None), size=(650, 500),
                                   background = ''
                                   )
        close_button.bind(on_press=self.history_popup.dismiss)
        self.history_popup.open()

    def change_theme_button(self, instance):
        self.reset_user_entry()
        if self._light_theme:
            Window.clearcolor = (0, 0, 0, 0)
            if instance != "new":
                self.infobox.text = "applied dark theme!"
            self._light_theme = False
        else:
            Window.clearcolor = (1, 1, 1, 1)
            self._light_theme = True
            self.infobox.text = "applied light theme!"
        self.save_preferences()


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    MyApp().run()


if __name__ == '__main__':
    main()
