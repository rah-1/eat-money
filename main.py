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

        self.first_click = False

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
        self.user = TextInput(
            multiline=False,
            padding_y=(20, 20),
            size_hint=(1, 0.5)
        )

        self.window.add_widget(self.user)

        # button widget
        self.button = Button(
            text="SUBMIT FOOD",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#00FFCE',
            # remove darker overlay of background colour
            # background_normal = ""
        )
        self.button.bind(on_press=self.bigbuttonpress)
        self.window.add_widget(self.button)

        # button widget
        self.statsbutton = Button(
            text="VIEW STATS",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#00FFCE',
            # remove darker overlay of background colour
            # background_normal = ""
        )
        self.statsbutton.bind(on_press=self.viewstatsbutton)
        self.window.add_widget(self.statsbutton)

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


    def bigbuttonpress(self, instance):
        if self.first_click:
            self.button.text = "SUBMIT FOOD"
            self._curr_cost = self.user.text
            self.first_click = False

            # add food
            curr_food = Food(self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, 100)
            data_entry = [self._today.strftime("%d/%m/%Y"), self._curr_name, self._curr_cost, 100]
            self._food_list.append(curr_food)
            self.add_new_data(data_entry)

        else:
            self.button.text = "SUBMIT COST"
            self._curr_name = self.user.text
            self.first_click = True
        self.user.text = ""

    # todo: when stats button is preessed (popup???)
    def viewstatsbutton(self, instance):
        pass


if __name__ == '__main__':
    MyApp().run()
