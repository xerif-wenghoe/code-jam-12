import math

from js import document

from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

KNOB_RADIUS = 120
OUTER_RADIUS = 200
TICK_CHOICES = (
    (12, (1, 1, 1)),
    (24, (3, 1, 1)),
    (64, (8, 4, 1)),
    (72, (6, 3, 1)),
    (100, (10, 5, 1)),
)
TICKS, TICK_INTERVALS = TICK_CHOICES[2]
TICK_LENGTHS = (25, 20, 10)
TICK_WIDTHS = (3, 2, 1)
GREY_GRADIENT = (int("0x33", 16), int("0xAA", 16))
KNOB_SLICES = 180
TWO_PI = 2 * math.pi
MOUSE_DEADZONE_RADIUS = 7


class SafeMethod:
    byte = 0x04
    static_id = "safe"
    name = "Safe"
    description = "A safe combination"

    on_key_received: KeyReceiveCallback | None = None

    @staticmethod
    def grey(frac: float) -> str:
        return (
            "#"
            + f"{int(frac * GREY_GRADIENT[1] + (1 - frac) * GREY_GRADIENT[0]):02x}" * 3
        )

    async def setup(self) -> None:  # noqa: PLR0915
        self.combination = []
        self.last_mousedown = None  # angle at which the mouse was clicked
        self.last_dial_value = 0  # value at which the dial was previously left at
        self.prev_angle = None  # angle at which the mouse was last detected
        self.total_angle = None

        self.offscreen_canvas = document.createElement("canvas")
        self.offscreen_canvas.width = 600
        self.offscreen_canvas.height = 400
        ctx = self.offscreen_canvas.getContext("2d")
        ctx.fillStyle = "#FFFFFF"
        ctx.translate(self.offscreen_canvas.width / 2, self.offscreen_canvas.height / 2)

        self.dial_canvas = elem_by_id("dial-canvas")
        self.dial_canvas.style.zIndex = 1
        ctx = self.dial_canvas.getContext("2d")
        ctx.fillStyle = "#FFFFFF"
        ctx.translate(self.dial_canvas.width / 2, self.dial_canvas.height / 2)

        self.static_canvas = elem_by_id("static-canvas")
        self.static_canvas.style.zIndex = 0
        ctx = self.static_canvas.getContext("2d")
        ctx.fillRect(0, 0, self.static_canvas.width, self.static_canvas.height)
        ctx.translate(self.static_canvas.width / 2, self.static_canvas.height / 2)
        ctx.fillStyle = "#FFFFFF"

        self.dial_input_range = elem_by_id("dial-num")

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
            ctx.strokeStyle = ctx.fillStyle = SafeMethod.grey(
                1 - ((sin2x + cos4x) ** 2) / 4,
            )
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
        self.output_div = elem_by_id("output")

        add_event_listener(self.dial_canvas, "mousedown", self.on_mouse_down)
        add_event_listener(self.dial_canvas, "mousemove", self.on_mouse_move)
        add_event_listener(self.dial_canvas, "mouseup", self.on_mouse_up)
        add_event_listener(self.dial_input_range, "input", self.change_dial_type)

        self.btn_reset = elem_by_id("btn-reset")
        add_event_listener(self.btn_reset, "click", self.reset_combination)

    def align_center(self) -> None:
        self.div.style.alignItems = "center"

    def prerender_ticks(self) -> None:
        ctx = self.offscreen_canvas.getContext("2d")
        w, h = self.offscreen_canvas.width, self.offscreen_canvas.height
        ctx.clearRect(-w / 2, -h / 2, w, h)
        ctx.save()
        for tick in range(TICKS):
            ctx.save()
            ctx.beginPath()
            ctx.rotate(TWO_PI * tick / TICKS)
            for t_type, interval in enumerate(TICK_INTERVALS):
                if tick % interval != 0:
                    continue
                ctx.roundRect(
                    -TICK_WIDTHS[t_type] / 2,
                    -OUTER_RADIUS + 4,
                    TICK_WIDTHS[t_type],
                    TICK_LENGTHS[t_type],
                    TICK_WIDTHS[t_type] / 2,
                )
                break
            ctx.fill()
            ctx.restore()

        ctx.font = "24px sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "top"
        for tick_numbering in range(0, TICKS, TICK_INTERVALS[0]):
            ctx.save()
            ctx.beginPath()
            ctx.rotate(TWO_PI * tick_numbering / TICKS)
            ctx.fillText(
                str(tick_numbering),
                0,
                -OUTER_RADIUS + 4 + TICK_LENGTHS[0] + 5,
            )
            ctx.restore()
        ctx.restore()

    def draw_ticks(self, angle: float = 0.0) -> None:
        w, h = self.dial_canvas.width, self.dial_canvas.height
        ctx = self.dial_canvas.getContext("2d")
        ctx.clearRect(-w / 2, -h / 2, w, h)
        ctx.save()
        ctx.rotate(angle)
        ctx.drawImage(self.offscreen_canvas, -w / 2, -h / 2)
        ctx.restore()
        ctx.beginPath()
        ctx.moveTo(-5, -OUTER_RADIUS - 5)
        ctx.lineTo(5, -OUTER_RADIUS - 5)
        ctx.lineTo(0, -OUTER_RADIUS + 25)
        ctx.closePath()
        ctx.fillStyle = "#EE0000"
        ctx.strokeStyle = "#660000"
        ctx.fill()
        ctx.stroke()

    def get_mouse_coords(self, event: object) -> None:
        rect = self.dial_canvas.getBoundingClientRect()
        mx = event.clientX - rect.left - rect.width // 2
        my = event.clientY - rect.top - rect.height // 2
        return mx, my

    def on_mouse_down(self, event: object) -> None:
        if self.total_angle is not None:
            self.register_knob_turn()
            return
        mx, my = self.get_mouse_coords(event)
        if mx**2 + my**2 > OUTER_RADIUS**2:
            return
        self.total_angle = 0
        self.last_mousedown = ((mx, my), math.atan2(my, mx))

    def on_mouse_move(self, event: object) -> None:
        mx, my = self.get_mouse_coords(event)
        if self.last_mousedown is None:
            return
        curr_angle = math.atan2(my, mx)
        d_theta = curr_angle - self.last_mousedown[1]
        diff = self.total_angle - d_theta
        pi_diffs = abs(diff) // math.pi
        if pi_diffs % 2 == 1:
            pi_diffs += 1
        self.total_angle = d_theta + (-1 if diff < 0 else 1) * pi_diffs * math.pi
        self.draw_ticks(self.total_angle + self.last_dial_value * TWO_PI / TICKS)

    def on_mouse_up(self, event: object) -> None:
        if self.last_mousedown is None:
            return
        mx, my = self.get_mouse_coords(event)
        px, py = self.last_mousedown[0]
        if (px - mx) ** 2 + (py - my) ** 2 > MOUSE_DEADZONE_RADIUS**2:
            self.register_knob_turn()

    def change_dial_type(self, event: object) -> None:
        global TICKS, TICK_INTERVALS
        TICKS, TICK_INTERVALS = TICK_CHOICES[int(event.target.value)]
        self.prerender_ticks()
        self.reset_combination(event)

    async def register_knob_turn(self) -> None:
        val = (1 if self.total_angle >= 0 else -1) * round(
            abs(self.total_angle) * TICKS / TWO_PI,
        )
        self.combination.append(val)
        self.last_mousedown = None
        self.last_dial_value = (self.last_dial_value + val) % TICKS
        self.draw_ticks(self.last_dial_value * TWO_PI / TICKS)
        self.prev_angle = None
        self.total_angle = None
        if self.on_key_received is not None:
            await self.on_key_received(bytes(self.combination))

    async def reset_combination(self, _event: object) -> None:
        self.last_mousedown = None
        self.last_dial_value = 0
        self.draw_ticks()
        self.prev_angle = None
        self.total_angle = None
        self.combination = []
        if self.on_key_received is not None:
            await self.on_key_received(bytes(self.combination))
