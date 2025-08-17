from js import document, Image, Promise
from pyodide.ffi import create_proxy
import math
from textwrap import dedent

KNOB_RADIUS = 120
OUTER_RADIUS = 200
TICKS = 100
TICK_INTERVALS = (10, 5, 1)
TICK_LENGTHS = (25, 20, 10)
TICK_WIDTHS = (3, 2, 1)
GREY_GRADIENT = (int("0x33", 16), int("0xAA", 16))
KNOB_SLICES = 180
TWO_PI = 2 * math.pi


class SafeLock:

    @staticmethod
    def grey(frac):
        return "#" + f"{int(frac * GREY_GRADIENT[1] + (1 - frac) * GREY_GRADIENT[0]):02x}" * 3

    def __init__(self):

        self.combination = []
        self.last_mousedown = None  # angle at which the mouse was clicked
        self.last_dial_angle = 0  # angle at which the dial was previously left at
        self.prev_angle = None  # angle at which the mouse was last detected
        self.total_angle = None

        style = document.createElement("style")
        style.textContent = dedent("""
        #container {
            display: grid;
            place-items: center;
        }
        #container canvas {
            grid-area: 1 / 1;
        }
        """)
        document.head.appendChild(style)
        container = document.createElement("div")
        container.id = "container"
        self.div = document.createElement("div")
        self.div.style.alignItems = "center"
        self.div.appendChild(container)
        document.body.appendChild(self.div)
        self.knob_canvas = document.createElement("canvas")
        self.knob_canvas.width = 2 * OUTER_RADIUS + 20
        self.knob_canvas.height = 2 * OUTER_RADIUS + 40
        self.knob_canvas.style.zIndex = 0
        self.ticks_canvas = document.createElement("canvas")
        self.ticks_canvas.width = 2 * OUTER_RADIUS + 20
        self.ticks_canvas.height = 2 * OUTER_RADIUS + 40
        self.ticks_canvas.style.zIndex = 1
        self.ticks_canvas.getContext("2d").fillStyle = "#FFFFFF"
        self.ticks_canvas.getContext("2d").translate(self.ticks_canvas.width / 2, self.ticks_canvas.height / 2)
        container.appendChild(self.knob_canvas)
        container.appendChild(self.ticks_canvas)
        ctx = self.knob_canvas.getContext("2d")
        ctx.fillStyle = "#FFFFFF"
        ctx.fillRect(0, 0, self.knob_canvas.width, self.knob_canvas.height)
        ctx.translate(self.knob_canvas.width / 2, self.knob_canvas.height / 2)

        # draw outer dial
        ctx.save()
        radial_grad = ctx.createRadialGradient(0, 0, KNOB_RADIUS, 0, 0, OUTER_RADIUS)
        radial_grad.addColorStop(0.0, "#222222")
        radial_grad.addColorStop(0.7, "#000000")
        radial_grad.addColorStop(0.85, "#202020")
        radial_grad.addColorStop(0.96, "#444444")
        radial_grad.addColorStop(1, "#000000")
        ctx.beginPath()
        ctx.moveTo(OUTER_RADIUS, 0)
        ctx.arc(0, 0, OUTER_RADIUS, 0, TWO_PI)
        ctx.fillStyle = radial_grad
        ctx.fill()
        ctx.restore()
        
        # draw knob
        d_theta = TWO_PI / KNOB_SLICES
        for slc in range(KNOB_SLICES):
            theta = TWO_PI * slc / KNOB_SLICES
            ctx.save()
            ctx.rotate(theta)
            ctx.beginPath()
            ctx.moveTo(0, 0)
            ctx.lineTo(KNOB_RADIUS + (slc % 2) * 2, 0)
            ctx.arc(0, 0, KNOB_RADIUS + (slc % 2) * 2, 0, d_theta * 1.005)
            ctx.closePath()
            sin2x, cos4x = math.sin(2 * theta), math.cos(4 * theta)
            ctx.strokeStyle = ctx.fillStyle = SafeLock.grey(1 - ((sin2x + cos4x) ** 2) / 4)
            ctx.stroke()
            ctx.fill()
            ctx.restore()
        
        ctx.beginPath()
        ctx.moveTo(KNOB_RADIUS - 5, 0)
        ctx.arc(0, 0, KNOB_RADIUS - 5, 0, TWO_PI)
        ctx.moveTo(KNOB_RADIUS - 10, 0)
        ctx.arc(0, 0, KNOB_RADIUS - 10, 0, TWO_PI)
        ctx.strokeStyle = "#000000"
        ctx.stroke()

        self.prerender_ticks()
        self.draw_ticks()
        self.create_output_div()
        self.log_output("Hello!")

        for event, proxy in (("mousedown", self.on_mouse_down), ("mousemove", self.on_mouse_move), ("mouseup", self.on_mouse_up)):
            self.ticks_canvas.addEventListener(event, create_proxy(proxy))


    def prerender_ticks(self):
        self.offscreen_canvas = document.createElement("canvas")
        self.offscreen_canvas.width = 2 * OUTER_RADIUS + 20
        self.offscreen_canvas.height = 2 * OUTER_RADIUS + 40
        ctx = self.offscreen_canvas.getContext("2d")
        ctx.fillStyle = "#FFFFFF"
        ctx.translate(self.ticks_canvas.width / 2, self.ticks_canvas.height / 2)
        ctx.save()
        for tick in range(TICKS):
            ctx.save()
            ctx.beginPath()
            ctx.rotate(TWO_PI * tick / TICKS)
            for t_type, interval in enumerate(TICK_INTERVALS):
                if tick % interval == 0: break
            ctx.roundRect(0, OUTER_RADIUS - 4 - TICK_LENGTHS[t_type], TICK_WIDTHS[t_type], TICK_LENGTHS[t_type], TICK_WIDTHS[t_type])
            ctx.fill()
            ctx.restore()

        ctx.font = "24px sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "top"
        for tick_numbering in range(0, TICKS, TICK_INTERVALS[0]):
            ctx.save()
            ctx.beginPath()
            ctx.rotate(TWO_PI * tick_numbering / TICKS)
            ctx.fillText(str(tick_numbering), -1, -OUTER_RADIUS + 4 + TICK_LENGTHS[0] + 5)
            ctx.restore()
        ctx.restore()


    def draw_ticks(self, angle=0):
        w, h = self.ticks_canvas.width, self.ticks_canvas.height
        ctx = self.ticks_canvas.getContext("2d")
        ctx.clearRect(-w / 2, -h / 2, w, h)
        ctx.save()
        ctx.rotate(angle)
        ctx.drawImage(self.offscreen_canvas, -w / 2, -h / 2)
        ctx.restore()

    def create_output_div(self):
        # Create a div
        self.output_div = document.createElement("div")
        self.output_div.id = "output"
        self.output_div.style.height = "100px"
        self.output_div.style.border = "1px solid #ccc"
        self.output_div.style.padding = "0.5em"
        self.output_div.style.fontFamily = "monospace"
        self.output_div.style.overflowY = "auto"

        # Add it to the page
        self.div.appendChild(self.output_div)

    # Define a function to log
    def log_output(self, msg):
        self.output_div.innerHTML += msg + "<br>"
        self.output_div.scrollTop = self.output_div.scrollHeight  # auto-scroll


    def get_mouse_coords(self, event):
        rect = self.ticks_canvas.getBoundingClientRect()
        mx = event.clientX - rect.left - rect.width // 2 
        my = event.clientY - rect.top - rect.height // 2
        return mx, my


    def on_mouse_down(self, event):
        if self.total_angle is not None:
            self.register_knob_turn()
            return
        mx, my = self.get_mouse_coords(event)
        if mx ** 2 + my ** 2 > OUTER_RADIUS ** 2: return
        self.total_angle = 0
        self.last_mousedown = math.atan2(my, mx)


    def on_mouse_move(self, event):
        mx, my = self.get_mouse_coords(event)
        if self.last_mousedown is None:
            self.log_output(f"({mx, my}) angle: {math.atan2(my, mx)}")
            return
        curr_angle = math.atan2(my, mx)
        d_theta = curr_angle - self.last_mousedown
        diff = self.total_angle - d_theta
        pi_diffs = abs(diff) // math.pi
        if pi_diffs % 2 == 1: pi_diffs += 1
        self.total_angle = d_theta + (-1 if diff < 0 else 1) * pi_diffs * math.pi
        self.log_output(f"Total: {self.total_angle}")
        self.draw_ticks(self.total_angle + self.last_dial_angle)


    def on_mouse_up(self, event):
        mx, my = self.get_mouse_coords(event)
        if self.last_mousedown != (mx, my):
            self.register_knob_turn()

    def register_knob_turn(self):
        pass