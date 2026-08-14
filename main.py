from kivy.lang import Builder
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField

# این import ها لازم‌اند تا kv کلاس‌ها را بشناسد
from board import Board
from node import CircleNode
from database import init_db, load_nodes


class CaseBoardApp(MDApp):
    sidebar_open = False
    dialog = None

    def build(self):
        init_db()
        self.theme_cls.theme_style = "Dark"
        root_widget = Builder.load_file("caseboard.kv")
    
        board = root_widget.ids.board
        for node_id, name, x, y in load_nodes():
            node = CircleNode(
                person_name = name,
                pos=(x, y),
                db_id = node_id,
            )
            board.register_node(node)
        board.load_saved_connections()
        return root_widget

    # ---------- Sidebar ----------
    def toggle_sidebar(self):
        sidebar = self.root.ids.sidebar
        if self.sidebar_open:
            anim = Animation(width=0, opacity=0, d=.25, t="out_cubic")
        else:
            anim = Animation(width=dp(170), opacity=1, d=.25, t="out_cubic")
        anim.start(sidebar)
        self.sidebar_open = not self.sidebar_open

    # ---------- Add Person ----------
    def open_add_dialog(self):
        self.name_field = MDTextField(hint_text="Person name")
        # با زدن Enter هم اضافه شود
        self.name_field.bind(on_text_validate=self.confirm_add)
        self.dialog = MDDialog(
            title="Add Person",
            type="custom",
            content_cls=self.name_field,
            buttons=[
                MDFlatButton(text="CANCEL",
                             on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=self.confirm_add),
            ],
        )
        self.dialog.open()

    def confirm_add(self, *_):
        name = self.name_field.text.strip()
        if name:
            self.root.ids.board.add_node(name)
        self.dialog.dismiss()

    # ---------- Add Connection ----------
    def start_add_connection(self):
        self.root.ids.board.start_connection_mode()

    # ---------- Delete ----------
    def toggle_delete_mode(self):
        board = self.root.ids.board
        if board.delete_mode:
            board.cancel_delete_mode()
        else:
            board.start_delete_mode()

    # ---------- Edit ----------
    def toggle_edit_mode(self):
        board = self.root.ids.board
        if board.edit_mode:
            board.cancel_edit_mode()
        else:
            board.start_edit_mode()


if __name__ == "__main__":
    CaseBoardApp().run()
