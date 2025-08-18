from collections.abc import Callable
from typing import Any

from js import Promise, window, setTimeout, setInterval, clearInterval


from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

#FIX!!!
from pyodide.ffi import create_proxy

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
    byte = 0x02
    static_id = "music"
    name = "Music"
    description = "A song"

    on_key_received: KeyReceiveCallback | None = None
    grid: list[list[str | None]]

    async def setup(self) -> None:
        
        #
        self.canvas = elem_by_id("instrument-canvas")
        self.playButton = elem_by_id("play-button")
        self.bpmSlider = elem_by_id("bpm-slider")
        self.bpmDisplay = elem_by_id("bpm-display")
        self.ctx = self.canvas.getContext("2d")
        
        #
        #self.canvas.style.width = f"{window.screen.width*0.8}px"
        #self.canvas.style.height = f"{window.screen.height*0.8}px"
        #self.canvas.width = window.screen.width*0.8
        #self.canvas.height = window.screen.height*0.8
        self.ctx.imageSmoothingEnabled = False

        #
        self.rows = 16
        self.columns = 16

        # Create the grid data structure
        # SELF.GRID IS WHAT THE KEY SHOULD BE
        self.grid = []
        for _ in range(self.columns):
            column = []
            for _ in range(self.rows):
                column.append(-1)
            self.grid.append(column.copy())

        
        self.currentColumn = None
        self.playing = False
        
        self.bpm = 60
        self.interval = 60000/self.bpm

        self.width = self.canvas.width
        self.height = self.canvas.height
        self.boxWidth = self.width/self.columns
        self.boxHeight = self.height/self.rows 

        self._draw_grid()

        # Control buttons and handlers
        add_event_listener(self.canvas, "click", self._update_on_click)
        add_event_listener(self.playButton, "click", self._toggle_play)
        add_event_listener(self.bpmSlider, "change", self._change_bpm)
        await self.load_notes()

    # LEARN BETTER LOADING copied from chess
    async def load_notes(self) -> None:
        def load_sound(src: str) -> object:
            def executor(
                resolve: Callable[[object], None],
                _reject: Callable[[object], None],
            ) -> None:
                sound = window.Audio.new()  # pyright: ignore[reportAttributeAccessIssue]
                sound.onloadeddata = lambda *_, sound=sound: resolve(sound)
                sound.src = src
            return Promise.new(executor)  # pyright: ignore[reportAttributeAccessIssue]

        note_names = [
            f"Piano.{i}"
            for i in range(7, 23)
        ]
        
        self.notes = {}
        for note_name in note_names:
            self.notes[note_name] = await load_sound(f"/methods/music/audio/{note_name}.mp3")
            
        self.tick_proxy = create_proxy(self._tick) # It only works with this for some reason instead of @create_proxy
    
    # Main event loop, calls self
    # TODO: REFACTOR setTimeout
    def _tick(self):
        self._play_notes(self.grid[self.currentColumn])
        self._draw_grid()
        self.currentColumn = (self.currentColumn + 1) % self.columns
        setTimeout(self.tick_proxy, self.interval)
        

    def _play_note(self, noteName: str) -> None:
        notefound = self.notes[f"Piano.{noteName}"]
        notefound.currentTime = 0
        notefound.play()
        print("playing note", notefound)

    def _play_notes(self, grid_section: list) -> None:
        for number, on in enumerate(grid_section):
            if on == 1:
                self._play_note(f"{self.rows-number+7-1}") # make more clear
        print(grid_section)
        

    def _update_on_click(self, event: object) -> None:
        rect_canvas = self.canvas.getBoundingClientRect()
        click_x = event.clientX - rect_canvas.left
        click_y = event.clientY - rect_canvas.top

        columnClicked = int(click_x/self.boxWidth)    
        rowClicked = int(click_y/self.boxHeight) 
        try:
            self.grid[columnClicked][rowClicked] *= -1
            print(f"p{rowClicked}")
            if self.grid[columnClicked][rowClicked] == 1:
                self._play_note(f"{self.rows-rowClicked+7-1}")
        except:
            print("errror")
            pass
        self._draw_grid()
            
    # look into intervalevents
    def _toggle_play(self, event: object) -> None:
        self.playing = not self.playing
        if self.playing:
            self.playButton.innerText = "⏸"
            self.currentColumn = 0
            self._tick()
        else:
            self.playButton.innerText = "▶"
        self._draw_grid()
            
    def _change_bpm(self, event: object):
        self.bpm = int(event.target.value)
        self.interval = 60000/self.bpm
        self.bpmDisplay.innerText = f"BPM: {self.bpm}"
        

    # Draw the music grid (should pr)
    def _draw_grid(self) -> None:
        color_dict = {
            0:"pink",
            1:"purple",
            2:"blue",
            3:"green",
            4:"yellow",
            5:"orange",
            6:"red"
        }

        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        h = round(self.boxHeight)
        w = round(self.boxWidth)
        self.ctx.lineWidth = 1

        # Draw the boxes
        for columnNumber, column in enumerate(self.grid):
            for rowNumber, row in enumerate(column):
                if row == 1:
                    self.ctx.beginPath()
                    self.ctx.rect(round(columnNumber*self.boxWidth),round(rowNumber*self.boxHeight), w, h)
                    self.ctx.fillStyle = color_dict[rowNumber%7]
                    self.ctx.fill()
                elif columnNumber == self.currentColumn and self.playing:
                    self.ctx.beginPath()
                    self.ctx.rect(round(columnNumber*self.boxWidth),round(rowNumber*self.boxHeight), w, h)
                    self.ctx.fillStyle = "grey"
                    self.ctx.fill()   

        # Draw the lines
        for i in range(self.rows):
            if i > 0:
                self.ctx.beginPath()
                self.ctx.strokeStyle = "grey"
                self.ctx.moveTo(0, round(i*self.boxHeight))
                self.ctx.lineTo(self.canvas.width, round(i*self.boxHeight))
                self.ctx.stroke()
        
        for i in range(self.columns):
            if i > 0:
                self.ctx.beginPath()
                if i%2 ==0: 
                    self.ctx.lineWidth = 1
                    self.ctx.strokeStyle = "white"
                else:
                    self.ctx.lineWidth = 1
                    self.ctx.strokeStyle = "grey"
                
                self.ctx.moveTo(round(i*self.boxWidth), 0)
                self.ctx.lineTo(round(i*self.boxWidth), self.canvas.height)
                self.ctx.stroke()

