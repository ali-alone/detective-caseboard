# Detective Caseboard

A simple detective-style case board app built with **Python**, **Kivy**, and **KivyMD**. Runs on both **PC** and **Android**.

Add people as circular profile nodes on a board, connect them with red lines to show relationships, and label those connections with text describing how they're linked.

## Features

- **Add Person** — create a new circular node on the board with a name.
- **Add Connection** — tap two person nodes to link them with a red line, then add a text label describing the relationship.
- **Edit Mode** — move nodes around the board and update their details.
- **Delete Mode** — remove nodes or connections you no longer need.
- **Sidebar** — organize work into separate cases/files (e.g. "File 1", "File 2").
- **Persistent storage** — nodes and connections are saved locally to a SQLite database (`caseboard.db`) so your board is restored on the next launch.

## Tech Stack

- [Python](https://www.python.org/)
- [Kivy](https://kivy.org/) — cross-platform UI framework
- [KivyMD](https://github.com/kivymd/KivyMD) — Material Design widgets for Kivy
- SQLite — local persistence

## Project Structure

```
.
├── main.py          # App entry point, sidebar, dialogs, mode toggles
├── board.py          # Board widget: node/connection management, modes
├── node.py           # Circular person node widget
├── connection.py      # Connection line between two nodes
├── database.py        # SQLite init and load/save helpers
└── caseboard.kv        # KivyMD layout (header, sidebar, board)
```

## Getting Started

### Requirements

- Python 3.9+
- [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html)
- [KivyMD](https://github.com/kivymd/KivyMD)

### Install

```bash
pip install kivy kivymd
```

### Run

```bash
python main.py
```

## Building for Android

This project can be packaged for Android using [Buildozer](https://github.com/kivy/buildozer):

```bash
pip install buildozer
buildozer init
buildozer -v android debug
```

## Roadmap

- [ ] Profile pictures for person nodes
- [ ] Multiple independent case files
- [ ] Export/import case boards

## License

No license specified yet.
