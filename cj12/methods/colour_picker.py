from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

COLOUR_HEX = {
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
}


class ColourPickerMethod:
    byte = 0x08
    static_id = "colour_picker"
    name = "Colour Picker Lock"
    description = "A colour hex code lock"

    on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None:
        self.is_mouse_down: bool = False
        self.hexcodes: dict[str, str] = {
            "red": "00",
            "green": "00",
            "blue": "00",
        }

        self.red_canvas = elem_by_id("red-canvas")
        self.green_canvas = elem_by_id("green-canvas")
        self.blue_canvas = elem_by_id("blue-canvas")
        self.red_ctx = self.red_canvas.getContext("2d", {"willReadFrequently": True})
        self.green_ctx = self.green_canvas.getContext(
            "2d",
            {"willReadFrequently": True},
        )
        self.blue_ctx = self.blue_canvas.getContext("2d", {"willReadFrequently": True})

        self.RGB_canvas = [self.red_canvas, self.blue_canvas, self.green_canvas]
        self.RGB_ctx = [self.red_ctx, self.green_ctx, self.blue_ctx]
        self.RGB = self.hexcodes.keys()

        self.setup_canvas()
        self.setup_event_listener()

    def setup_canvas(self) -> None:
        for canvas, ctx, colour in zip(
            self.RGB_canvas,
            self.RGB_ctx,
            self.RGB,
            strict=False,
        ):
            gradient = ctx.createLinearGradient(0, 0, canvas.width - 1, 0)
            gradient.addColorStop(0, "black")
            gradient.addColorStop(1, COLOUR_HEX[colour])
            ctx.fillStyle = gradient
            ctx.fillRect(0, 0, canvas.width, canvas.height)

    def setup_event_listener(self) -> None:
        def mouse_down(_evt: object) -> None:
            self.is_mouse_down = True

        async def mouse_up(_evt: object) -> None:
            self.is_mouse_down = False
            if self.on_key_received is not None:
                await self.on_key_received("".join(self.hexcodes.values()).encode())

        async def on_click(evt: object) -> None:
            self.update_colour(evt)
            if self.on_key_received is not None:
                await self.on_key_received("".join(self.hexcodes.values()).encode())

        for canvas in self.RGB_canvas:
            add_event_listener(canvas, "mousedown", mouse_down)
            add_event_listener(canvas, "mousemove", self.on_move)
            add_event_listener(canvas, "mouseup", mouse_up)
            add_event_listener(canvas, "click", on_click)
            add_event_listener(canvas, "mouseleave", mouse_up)

    def on_move(self, evt: object) -> None:
        if not self.is_mouse_down:
            return

        self.update_colour(evt)

    def update_colour(self, evt: object) -> None:
        canvas = evt.target
        for idx, colour in enumerate(self.hexcodes.keys()):
            if canvas.id == f"{colour}-canvas":
                pixel = (
                    self.RGB_ctx[idx].getImageData(evt.offsetX, evt.offsetY, 1, 1).data
                )

                self.hexcodes[colour] = hex(pixel[idx])[2:].zfill(2)

        self.update_display()

    def update_display(self) -> None:
        hexcode = "#" + "".join(self.hexcodes.values())
        elem_by_id("output-colour").style.backgroundColor = hexcode
        elem_by_id("output-value").innerText = hexcode.upper()
