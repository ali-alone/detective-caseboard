import random
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
from kivy.properties import BooleanProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from node import CircleNode
from connection import EdgeLabel
from database import (
    save_node,
    save_connection,
    load_connections,
    update_connection_label,
    delete_node,
    delete_connection,
    update_node_name,
)


class Board(FloatLayout):
    """بوم اصلی؛ گره‌ها اینجا اضافه می‌شوند."""

    connection_mode = BooleanProperty(False)
    delete_mode = BooleanProperty(False)
    edit_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nodes_by_id = {}
        self._connections = []
        self._pending_first_node = None
        self._label_dialog = None
        self._active_entry = None
        self._edit_dialog = None
        self._active_node = None

    def add_node(self, name):
        # موقعیت را با pixel محاسبه می‌کنیم، نه pos_hint،
        # چون pos_hint هر بار Board دوباره layout شود (مثلا موقع
        # انیمیشن سایدبار یا ریسایز پنجره) موقعیت درگ‌شده را ریست می‌کند.
        w, h = self.size if self.size != [0, 0] else (800, 600)
        x = random.uniform(.05, .75) * w
        y = random.uniform(.10, .70) * h
        node_id = save_node(name, x, y)
        node = CircleNode(person_name=name, pos=(x, y), db_id = node_id)
        self.register_node(node)
        return node

    def register_node(self, node):
        """گره را به بورد اضافه می‌کند و برای به‌روزرسانی خطوط اتصال pos را bind می‌کند."""
        self.add_widget(node)
        if node.db_id:
            self._nodes_by_id[node.db_id] = node
        node.bind(pos=self._on_node_moved)

    def load_saved_connections(self):
        for conn_id, a_id, b_id, label in load_connections():
            node_a = self._nodes_by_id.get(a_id)
            node_b = self._nodes_by_id.get(b_id)
            if node_a and node_b:
                self._draw_connection(conn_id, node_a, node_b, label)

    # ---------- Connection mode ----------
    def start_connection_mode(self):
        self.connection_mode = True
        self._pending_first_node = None
        for node in self._nodes_by_id.values():
            node.set_selected(False)

    def cancel_connection_mode(self):
        self.connection_mode = False
        if self._pending_first_node:
            self._pending_first_node.set_selected(False)
        self._pending_first_node = None

    # ---------- Delete mode ----------
    def start_delete_mode(self):
        self.delete_mode = True
        self.connection_mode = False
        self._pending_first_node = None

    def cancel_delete_mode(self):
        self.delete_mode = False

    # ---------- Edit mode ----------
    def start_edit_mode(self):
        self.edit_mode = True
        self.connection_mode = False
        self.delete_mode = False
        self._pending_first_node = None

    def cancel_edit_mode(self):
        self.edit_mode = False

    def node_tapped_for_edit(self, node):
        self.edit_mode = False
        self._active_node = node
        self._name_field = MDTextField(hint_text="Person name", text=node.person_name)
        self._name_field.bind(on_text_validate=self._confirm_edit_name)
        self._edit_dialog = MDDialog(
            title="Edit Person",
            type="custom",
            content_cls=self._name_field,
            buttons=[
                MDFlatButton(text="CANCEL",
                             on_release=lambda *_: self._edit_dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=self._confirm_edit_name),
            ],
        )
        self._edit_dialog.open()

    def _confirm_edit_name(self, *_):
        name = self._name_field.text.strip()
        node = self._active_node
        if name and node:
            node.person_name = name
            if node.db_id:
                update_node_name(node.db_id, name)
        self._edit_dialog.dismiss()
        self._active_node = None

    def node_tapped_for_delete(self, node):
        self.delete_mode = False
        for entry in list(self._connections):
            if entry["node_a"] is node or entry["node_b"] is node:
                self._remove_connection(entry)
        if node.db_id in self._nodes_by_id:
            del self._nodes_by_id[node.db_id]
        self.remove_widget(node)
        if node.db_id:
            delete_node(node.db_id)

    def edge_tapped_for_delete(self, entry):
        self.delete_mode = False
        self._remove_connection(entry)
        delete_connection(entry["id"])

    def _remove_connection(self, entry):
        self.canvas.before.remove(entry["color"])
        self.canvas.before.remove(entry["line"])
        self.remove_widget(entry["edge_label"])
        if entry in self._connections:
            self._connections.remove(entry)

    def node_tapped(self, node):
        if not self._pending_first_node:
            self._pending_first_node = node
            node.set_selected(True)
            return
        if node is self._pending_first_node:
            return
        node_a = self._pending_first_node
        node_b = node
        node_a.set_selected(False)
        self._pending_first_node = None
        self.connection_mode = False

        conn_id = save_connection(node_a.db_id, node_b.db_id)
        self._draw_connection(conn_id, node_a, node_b, "")

    def _draw_connection(self, conn_id, node_a, node_b, label):
        with self.canvas.before:
            color = Color(0.9, 0.1, 0.1, 1)
            line = Line(points=self._line_points(node_a, node_b), width=1.6)
        edge_label = EdgeLabel(connection_id=conn_id, text=label)
        edge_label.pos = self._label_pos(node_a, node_b)
        edge_label.bind(on_release=lambda *_: self._edge_label_pressed(entry))
        self.add_widget(edge_label)
        entry = {
            "id": conn_id,
            "node_a": node_a,
            "node_b": node_b,
            "label": label,
            "line": line,
            "color": color,
            "edge_label": edge_label,
        }
        self._connections.append(entry)
        return entry

    def _edge_label_pressed(self, entry):
        if self.delete_mode:
            self.edge_tapped_for_delete(entry)
        else:
            self.edit_connection_label(entry)

    def _line_points(self, node_a, node_b):
        ax, ay = node_a.get_center()
        bx, by = node_b.get_center()
        return [ax, ay, bx, by]

    def _label_pos(self, node_a, node_b):
        ax, ay = node_a.get_center()
        bx, by = node_b.get_center()
        mid_x = (ax + bx) / 2
        mid_y = (ay + by) / 2
        return (mid_x - 50, mid_y - 10)

    def _on_node_moved(self, moved_node, _pos):
        for entry in self._connections:
            if entry["node_a"] is moved_node or entry["node_b"] is moved_node:
                entry["line"].points = self._line_points(entry["node_a"], entry["node_b"])
                entry["edge_label"].pos = self._label_pos(entry["node_a"], entry["node_b"])

    # ---------- Connection label editing ----------
    def edit_connection_label(self, entry):
        self._active_entry = entry
        self._label_field = MDTextField(
            hint_text="Relationship / note",
            text=entry["label"],
        )
        self._label_field.bind(on_text_validate=self._confirm_label)
        self._label_dialog = MDDialog(
            title="Connection Info",
            type="custom",
            content_cls=self._label_field,
            buttons=[
                MDFlatButton(text="CANCEL",
                             on_release=lambda *_: self._label_dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=self._confirm_label),
            ],
        )
        self._label_dialog.open()

    def _confirm_label(self, *_):
        text = self._label_field.text.strip()
        entry = self._active_entry
        entry["label"] = text
        entry["edge_label"].text = text
        update_connection_label(entry["id"], text)
        self._label_dialog.dismiss()
        self._active_entry = None
