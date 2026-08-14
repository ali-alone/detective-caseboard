from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.properties import NumericProperty


class EdgeLabel(ButtonBehavior, Label):
    """Clickable text label placed at the midpoint of a connection line."""

    connection_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 20)
        self.font_size = 12
        self.color = (1, 1, 1, 1)
        self.bold = True
