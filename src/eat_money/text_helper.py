input_helper = """
MDTextField:
    hint_text: "Enter info"
    helper_text: "press enter to submit"
    helper_text_mode: "on_focus"
    multiline:False
"""

date_helper = """
MDTextField:
    hint_text: "Enter Date"
    helper_text: "YYYY-MM-DD"
    helper_text_mode: "persistent"
    multiline:False
"""

food_helper = """
MDTextField:
    hint_text: "Enter Food"
    helper_text_mode: "on_focus"
    multiline:False
"""

cost_helper = """
MDTextField:
    hint_text: "Enter Cost"
    helper_text_mode: "on_focus"
    multiline:False
"""

list_helper = """
MDSelectionList:
    id: selection_list
    spacing: "12dp"
    overlay_color: app.theme_color[:-1] + [.2]
    icon_bg_color: app.theme_color
    on_selected: app.on_selected(*args)
    on_unselected: app.on_unselected(*args)
    progress_round_color: app.theme_color
    progress_round_size: "35dp"
    size_hint: 1.0 , None 
"""

change_dialog = """
MDBoxLayout:
    
    GridLayout:
        rows: 3
        md_bg_color: 0,0,0,1
        MDTextField:
            hint_text: "Enter Date"
            helper_text: "YYYY-MM-DD"
            helper_text_mode: "persistent"
            multiline:False
        
        MDTextField:
            hint_text: "Enter Food Name(s)"
            helper_text: "Only Enter One Item"
            helper_text_mode: "on_focus"
            multiline:False
            
        MDTextField:
            hint_text: "Enter Cost"
            helper_text_mode: "on_focus"
            multiline:False

    BoxLayout:
        orientation: 'horizontal'
    
        MDRaisedButton:
            text: "SAVE"
            on_release: app.update_entry()
        MDFlatButton:
            text: 'CANCEL'
            on_release: app.close_dialog()
        
"""


