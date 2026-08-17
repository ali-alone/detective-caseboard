from kivy.properties import StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.label import Label
from kivy.app import App
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

    def on_parent(self, _widget, parent):
        if parent:
            parent.bind(size=self._keep_inside_board)

    def _bounded_position(self, x, y):
        board = self.parent
        if board is None:
            return x, y

        left_boundary = self._sidebar_boundary(board)
        max_y = max(0, board.height - self.height)
        return max(x, left_boundary), min(max(y, 0), max_y)

    def _sidebar_boundary(self, board):
        app = App.get_running_app()
        root = app.root if app else None
        sidebar = root.ids.get("sidebar") if root else None

        if sidebar is None:
            return 0

        sidebar_right_x = sidebar.to_window(sidebar.width, 0)[0]
        board_bottom_y = board.to_window(0, 0)[1]
        return max(0, board.to_widget(sidebar_right_x, board_bottom_y)[0])

    def _keep_inside_board(self, *_):
        self.pos = self._bounded_position(self.x, self.y)

    def on_touch_down(self, touch):
        board = self.parent
        if board is None:
            return super().on_touch_down(touch)

        local_touch = board.to_widget(*touch.pos)
        if self.collide_point(*local_touch):
            if board is not None and getattr(board, "delete_mode", False):
                board.node_tapped_for_delete(self)
                return True
            if board is not None and getattr(board, "edit_mode", False):
                board.node_tapped_for_edit(self)
                return True
            if board is not None and getattr(board, "connection_mode", False):
                board.node_tapped(self)
                return True
            touch.grab(self)
            self._drag_offset = (
                local_touch[0] - self.x,
                local_touch[1] - self.y,
            )
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            local_touch = self.parent.to_widget(*touch.pos)
            self.pos = self._bounded_position(
                local_touch[0] - self._drag_offset[0],
                local_touch[1] - self._drag_offset[1],
            )
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
