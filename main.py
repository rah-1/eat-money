from datetime import date
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyApp(App):
    def build(self):
        self.first_click = True

        today = date.today().strftime("%B %d, %Y")
        print("Today's date:", today)

        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # logo widget (todo)
        # self.window.add_widget(Image(source="filename.png"))

        # label widget
        self.greeting = Label(
            text="EAT MONEY\n" + today,
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

    def bigbuttonpress(self, instance):
        if self.first_click:
            self.button.text = "SUBMIT COST"
            self.first_click = False
        else:
            self.button.text = "SUBMIT FOOD"
            self.first_click = True
        self.user.text = ""


    def viewstatsbutton(self, instance):
        pass


if __name__ == '__main__':
    MyApp().run()
