from collections.abc import Callable

from js import Promise, clearTimeout, setTimeout, window
from pyodide.ffi import create_proxy

from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

# NOTES

# IMPORTANT
# Implement key system using self.grid
# Change grid size based on screen width
# Refactor setTimeout
# new art

# OTHER
# Refactor self.currentColumn and self.playing
# Refactor constants, note numbering system
# Refactor event loop to use dtime
# Refactor all canvas to account for dpi
# Refactor all canvas to account for subpixels

# LEARN
# look into BETTER ASYNC LOADING copied from chess
# look into intervalevents


class MusicMethod:
    byte = 0x07
    static_id = "music"
    name = "Music"
    description = "A song"

    on_key_received: KeyReceiveCallback | None = None
    grid: list[list[str | None]]

    async def setup(self) -> None:
        self.canvas = elem_by_id("instrument-canvas")
        self.playButton = elem_by_id("play-button")
        self.bpmSlider = elem_by_id("bpm-slider")
        self.bpmDisplay = elem_by_id("bpm-display")

        self.ctx = self.canvas.getContext("2d")
        self.ctx.imageSmoothingEnabled = False

        self.rows = 16
        self.columns = 32

        # Create the grid data structure
        # SELF.GRID IS WHAT THE KEY SHOULD BE
        self.grid = [[-1] * self.rows for _ in range(self.columns)]

        self.currentColumn = None
        self.playing = False

        self.bpm = 120
        self.interval = 60000 / self.bpm

        rect_canvas = self.canvas.getBoundingClientRect()
        self.canvas.width = self.width = rect_canvas.width
        self.canvas.height = self.height = rect_canvas.height
        self.box_width = self.width / self.columns
        self.box_height = self.height / self.rows

        self.timeout_calls = []

        self._draw_grid()

        # Control buttons and handlers
        add_event_listener(self.canvas, "click", self._update_on_click)
        add_event_listener(self.playButton, "click", self._toggle_play)
        add_event_listener(self.bpmSlider, "change", self._change_bpm)
        add_event_listener(window, "resize", self._height_setup)
        await self.load_notes()

    def resize_canvas(self, ratio: float) -> None:
        self.canvas.width = window.screen.width * ratio
        self.canvas.height = window.screen.height * ratio

    # LEARN BETTER LOADING copied from chess
    async def load_notes(self) -> None:
        def load_sound(src: str) -> object:
            def executor(
                resolve: Callable[[object], None],
                _reject: Callable[[object], None],
            ) -> None:
                sound = window.Audio.new()
                sound.onloadeddata = lambda *_, sound=sound: resolve(sound)
                sound.src = src

            return Promise.new(executor)

        note_names = [f"Piano.{i}" for i in range(7, 23)]

        self.notes = {}
        for note_name in note_names:
            self.notes[note_name] = await load_sound(
                f"/methods/music/audio/{note_name}.mp3",
            )

        self.tick_proxy = create_proxy(
            self._tick,
        )  # It only works with this for some reason instead of @create_proxy

    # Main event loop, calls self
    # TODO: REFACTOR setTimeout
    def _tick(self) -> None:
        if not self.playing or not elem_by_id("instrument-canvas"):
            return
        self._play_notes(self.grid[self.currentColumn])
        self._draw_grid()
        self.currentColumn = (self.currentColumn + 1) % self.columns
        self.timeout_calls.append(setTimeout(self.tick_proxy, self.interval))

    def _height_setup(self, _event: object) -> None:
        rect_canvas = self.canvas.getBoundingClientRect()
        self.canvas.width = self.width = rect_canvas.width
        self.canvas.height = self.height = rect_canvas.height
        self.box_width = self.width / self.columns
        self.box_height = self.height / self.rows
        self._draw_grid()

    def _play_note(self, note_name: str) -> None:
        notefound = self.notes[f"Piano.{note_name}"]
        notefound.currentTime = 0
        notefound.play()

    def _play_notes(self, grid_section: list) -> None:
        for number, on in enumerate(grid_section):
            if on == 1:
                self._play_note(f"{self.rows - number + 7 - 1}")  # make more clear

    async def _update_on_click(self, event: object) -> None:
        key = self._flatten_list()
        await self.on_key_received(key.encode())
        rect_canvas = self.canvas.getBoundingClientRect()
        click_x = event.clientX - rect_canvas.left
        click_y = event.clientY - rect_canvas.top

        column_clicked = int(click_x / self.box_width)
        row_clicked = int(click_y / self.box_height)

        self.grid[column_clicked][row_clicked] *= -1
        if self.grid[column_clicked][row_clicked] == 1:
            self._play_note(f"{self.rows - row_clicked + 7 - 1}")
        self._draw_grid()

    def _flatten_list(self) -> str:
        return "".join(
            "1" if cell == 1 else "0" for column in self.grid for cell in column
        )

    # look into intervalevents
    def _toggle_play(self, _event: object) -> None:
        self.playing = not self.playing
        for timeout_call in self.timeout_calls:
            clearTimeout(timeout_call)
        if self.playing:
            self.playButton.innerText = "⏸"
            self.currentColumn = 0
            self._tick()
        else:
            self.playButton.innerText = "▶"

        self._draw_grid()

    def _change_bpm(self, event: object) -> None:
        self.bpm = int(event.target.value)
        self.interval = 60000 / self.bpm
        self.bpmDisplay.innerText = f"BPM: {self.bpm}"

    # Draw the music grid (should pr)
    def _draw_grid(self) -> None:
        color_dict = {
            0: "pink",
            1: "purple",
            2: "blue",
            3: "green",
            4: "yellow",
            5: "orange",
            6: "red",
        }

        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        h = round(self.box_height)
        w = round(self.box_width)
        self.ctx.lineWidth = 1

        # Draw the boxes
        for col_idx, column in enumerate(self.grid):
            for row_idx, row in enumerate(column):
                if row == 1:
                    self.ctx.beginPath()
                    self.ctx.rect(
                        round(col_idx * self.box_width),
                        round(row_idx * self.box_height),
                        w,
                        h,
                    )
                    self.ctx.fillStyle = color_dict[row_idx % 7]
                    self.ctx.fill()
                elif col_idx == self.currentColumn and self.playing:
                    self.ctx.beginPath()
                    self.ctx.rect(
                        round(col_idx * self.box_width),
                        round(row_idx * self.box_height),
                        w,
                        h,
                    )
                    self.ctx.fillStyle = "grey"
                    self.ctx.fill()

        # Draw the lines
        for i in range(self.rows):
            if i > 0:
                self.ctx.beginPath()
                self.ctx.strokeStyle = "grey"
                self.ctx.moveTo(0, round(i * self.box_height))
                self.ctx.lineTo(self.canvas.width, round(i * self.box_height))
                self.ctx.stroke()

        for i in range(self.columns):
            if i > 0:
                self.ctx.beginPath()
                if i % 2 == 0:
                    self.ctx.lineWidth = 1
                    self.ctx.strokeStyle = "white"
                else:
                    self.ctx.lineWidth = 1
                    self.ctx.strokeStyle = "grey"

                self.ctx.moveTo(round(i * self.box_width), 0)
                self.ctx.lineTo(round(i * self.box_width), self.canvas.height)
                self.ctx.stroke()
