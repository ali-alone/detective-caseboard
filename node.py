from kivy.properties import StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.label import Label
from database import update_node_pos


class CircleNode(FloatLayout):
    person_name = StringProperty("")
    db_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (80, 100)
        self.pos_hint = {}
        self._drag_offset = None
        self.selected = False

        with self.canvas:
            self._color = Color(0.3, 0.6, 1, 1)
            self._ellipse = Ellipse(pos=self._ellipse_pos(), size=(80, 80))

        self.bind(pos=self._update_graphics)

        self._label = Label(
            text=self.person_name,
            pos_hint={"center_x": 0.5 , "y": 0},
            size_hint=(None, None),
            size=(80, 20),
            font_size=12,
        )
        self.add_widget(self._label)
        self.bind(person_name=lambda inst, val: setattr(self._label, "text", val))

    def _ellipse_pos(self):
        return (self.x, self.y + 20)

    def _update_graphics(self, *args):
        self._ellipse.pos = self._ellipse_pos()

    def get_center(self):
        x, y = self._ellipse_pos()
        return (x + 40, y + 40)

    def set_selected(self, selected):
        self.selected = selected
        self._color.rgba = (1, 0.84, 0, 1) if selected else (0.3, 0.6, 1, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            board = self.parent
            if board is not None and getattr(board, "delete_mode", False):
                board.node_tapped_for_delete(self)
                return True
            if board is not None and getattr(board, "connection_mode", False):
                board.node_tapped(self)
                return True
            touch.grab(self)
            self._drag_offset = (touch.x - self.x, touch.y - self.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.pos = (touch.x - self._drag_offset[0],
                        touch.y - self._drag_offset[1])
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._drag_offset = None
            
            if self.db_id:
                update_node_pos(self.db_id,self.x, self.y)
                
            return True
        return super().on_touch_up(touch)
