from datetime import date
from food import Food
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import csv


class MyApp(App):
    def build(self):
        self._curr_name = ""
        self._curr_cost = ""

        # here: reads in old data upon build start
        self._food_list = []
        self.read_old_data()

        self._first_click = False

        self._today = date.today()
        print("Today's date:", self._today.strftime("%B %d, %Y"))

        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # todo: logo widget
        # self.window.add_widget(Image(source="filename.png"))

        # label widget
        self.greeting = Label(
            text="EAT MONEY\n" + self._today.strftime("%B %d, %Y"),
            font_size=36,
            color='#00FFCE',
            halign='center'
        )
        self.window.add_widget(self.greeting)

        # text input widget
        self.input_field = TextInput(
            multiline=False,
            padding_y=(20, 20),
            size_hint=(1, 0.5)
        )

        self.window.add_widget(self.input_field)

        # button widget
        self.submit_button = Button(
            text="SUBMIT FOOD",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#00FFCE',
            # remove darker overlay of background colour
            # background_normal = ""
        )
        self.submit_button.bind(on_press=self.big_button_press)
        self.window.add_widget(self.submit_button)

        # button widget
        self.stats_button = Button(
            text="VIEW STATS",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#00FFCE',
            # remove darker overlay of background colour
            # background_normal = ""
        )
        self.stats_button.bind(on_press=self.view_stats_button)
        self.window.add_widget(self.stats_button)

        # label widget
        self.infobox = Label(
            text="some info here!",
            font_size=14,
            color='#00FFCE',
            halign='center'
        )
        self.window.add_widget(self.infobox)

        return self.window

    # todo: this is a function to read in the csv file to load old data
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

    def add_new_data(self, data):
        with open('data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)


    def big_button_press(self, instance):
        if self._first_click:
            self.submit_button.text = "SUBMIT FOOD"
            self._curr_cost = self.input_field.text
            self._first_click = False

            # add food
            curr_food = Food(self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, 100)
            data_entry = [self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, 100]
            self._food_list.append(curr_food)
            self.add_new_data(data_entry)

        else:
            self.submit_button.text = "SUBMIT COST"
            self._curr_name = self.input_field.text
            self._first_click = True
        self.input_field.text = ""

    # todo: when stats button is preessed (popup???)
    def view_stats_button(self, instance):
        pass


if __name__ == '__main__':
    MyApp().run()
