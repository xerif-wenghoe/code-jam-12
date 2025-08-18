from dataclasses import dataclass
from math import atan2, cos, pi, sin, sqrt
from typing import ClassVar

from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

KNOB_RADIUS = 160
KNOB_CENTER_RADIUS = 25
DIRECTION_THRESHOLD = 40
CANVAS_SIZE = 400
MIN_DRAG_DISTANCE = 30


@dataclass
class Direction:
    name: str
    angle: float
    dx: int
    dy: int


class DirectionLockMethod:
    byte = 0x06
    static_id = "direction"
    name = "Direction Lock"
    description = "An 8-directional lock using a draggable knob"

    on_key_received: KeyReceiveCallback | None = None

    # Define the 8 directions
    DIRECTIONS: ClassVar[list[Direction]] = [
        Direction("top", -pi / 2, 0, -1),
        Direction("topright", -pi / 4, 1, -1),
        Direction("right", 0, 1, 0),
        Direction("bottomright", pi / 4, 1, 1),
        Direction("bottom", pi / 2, 0, 1),
        Direction("bottomleft", 3 * pi / 4, -1, 1),
        Direction("left", pi, -1, 0),
        Direction("topleft", -3 * pi / 4, -1, -1),
    ]

    async def setup(self) -> None:
        self.sequence: list[str] = []
        self.is_mouse_down: bool = False
        self.is_dragging: bool = False
        self.drag_start_x: float = 0
        self.drag_start_y: float = 0
        self.knob_center_x = CANVAS_SIZE // 2
        self.knob_center_y = CANVAS_SIZE // 2
        self.knob_offset_x = 0
        self.knob_offset_y = 0

        self.canvas = elem_by_id("direction-canvas")

        # Set canvas size for high DPI displays
        self.canvas.width = CANVAS_SIZE
        self.canvas.height = CANVAS_SIZE

        self.ctx = self.canvas.getContext("2d")

        self.output_textarea = elem_by_id("direction-output")

        # Setup control buttons
        self.btn_remove_last = elem_by_id("btn-remove-last")
        self.btn_reset_all = elem_by_id("btn-reset-all")

        # Add event listeners for buttons
        add_event_listener(self.btn_remove_last, "click", self.on_remove_last)
        add_event_listener(self.btn_reset_all, "click", self.on_reset_all)

        self.draw_knob()
        self.add_event_listeners()

    def draw_knob(self) -> None:  # noqa: PLR0915
        """Draw the knob with 8 direction indicators and the draggable center knob"""
        ctx = self.ctx
        ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

        # Draw main knob circle (background) - transparent
        ctx.beginPath()
        ctx.arc(self.knob_center_x, self.knob_center_y, KNOB_RADIUS, 0, 2 * pi)
        ctx.fillStyle = "rgba(240, 240, 240, 0.1)"  # Very transparent
        ctx.fill()
        ctx.strokeStyle = "rgba(51, 51, 51, 0.3)"  # Semi-transparent
        ctx.lineWidth = 2
        ctx.stroke()

        # Draw direction trails (gray paths)
        for direction in self.DIRECTIONS:
            # Calculate trail start and end points
            trail_start_x = self.knob_center_x + (KNOB_CENTER_RADIUS + 5) * cos(
                direction.angle,
            )
            trail_start_y = self.knob_center_y + (KNOB_CENTER_RADIUS + 5) * sin(
                direction.angle,
            )
            trail_end_x = self.knob_center_x + (KNOB_RADIUS - 15) * cos(direction.angle)
            trail_end_y = self.knob_center_y + (KNOB_RADIUS - 15) * sin(direction.angle)

            # Draw trail line
            ctx.beginPath()
            ctx.moveTo(trail_start_x, trail_start_y)
            ctx.lineTo(trail_end_x, trail_end_y)
            ctx.strokeStyle = "rgba(128, 128, 128, 0.4)"  # Semi-transparent gray
            ctx.lineWidth = 2
            ctx.stroke()

        # Draw direction indicators
        for direction in self.DIRECTIONS:
            # Calculate position on the knob edge
            x = self.knob_center_x + (KNOB_RADIUS - 10) * cos(direction.angle)
            y = self.knob_center_y + (KNOB_RADIUS - 10) * sin(direction.angle)

            # Draw direction indicator with highlight if dragging towards it
            ctx.beginPath()
            ctx.arc(x, y, 10, 0, 2 * pi)

            # Highlight the direction being targeted
            if self.is_dragging:
                # Get current mouse position for direction detection
                knob_x = self.knob_center_x + self.knob_offset_x
                knob_y = self.knob_center_y + self.knob_offset_y
                current_direction = self.get_direction_from_coords(knob_x, knob_y)
                if current_direction and current_direction.name == direction.name:
                    ctx.fillStyle = "rgba(70, 130, 180, 0.8)"  # Highlight color
                else:
                    ctx.fillStyle = "rgba(102, 102, 102, 0.6)"
            else:
                ctx.fillStyle = "rgba(102, 102, 102, 0.6)"
            ctx.fill()

            # Draw direction label
            ctx.fillStyle = "rgba(51, 51, 51, 0.8)"
            ctx.font = "14px Arial"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"

            # Position label outside the knob
            label_x = self.knob_center_x + (KNOB_RADIUS + 20) * cos(direction.angle)
            label_y = self.knob_center_y + (KNOB_RADIUS + 20) * sin(direction.angle)
            ctx.fillText(direction.name, label_x, label_y)

        # Draw the draggable center knob (light blue)
        knob_x = self.knob_center_x + self.knob_offset_x
        knob_y = self.knob_center_y + self.knob_offset_y

        # Add shadow effect
        ctx.beginPath()
        ctx.arc(knob_x + 3, knob_y + 3, KNOB_CENTER_RADIUS, 0, 2 * pi)
        ctx.fillStyle = "rgba(0, 0, 0, 0.3)"
        ctx.fill()

        # Draw main knob with different color when dragging
        ctx.beginPath()
        ctx.arc(knob_x, knob_y, KNOB_CENTER_RADIUS, 0, 2 * pi)
        if self.is_dragging:
            ctx.fillStyle = "rgba(95, 158, 160, 0.9)"  # Darker blue when dragging
        else:
            ctx.fillStyle = "rgba(135, 206, 235, 0.9)"  # Light blue
        ctx.fill()
        ctx.strokeStyle = "rgba(70, 130, 180, 0.8)"  # Steel blue border
        ctx.lineWidth = 3
        ctx.stroke()

        # Draw center dot
        ctx.beginPath()
        ctx.arc(knob_x, knob_y, 4, 0, 2 * pi)
        ctx.fillStyle = "rgba(51, 51, 51, 0.8)"
        ctx.fill()

        # Draw drag line when dragging
        if self.is_dragging and (self.knob_offset_x != 0 or self.knob_offset_y != 0):
            ctx.beginPath()
            ctx.moveTo(self.knob_center_x, self.knob_center_y)
            ctx.lineTo(knob_x, knob_y)
            ctx.strokeStyle = "rgba(70, 130, 180, 0.6)"
            ctx.lineWidth = 2
            ctx.setLineDash([5, 5])
            ctx.stroke()
            ctx.setLineDash([])  # Reset dash pattern

    def get_direction_from_coords(self, x: float, y: float) -> Direction | None:
        """Determine which direction the coordinates represent"""
        # Calculate distance from center
        dx = x - self.knob_center_x
        dy = y - self.knob_center_y
        distance = sqrt(dx * dx + dy * dy)

        # Check if within knob radius
        if distance < KNOB_RADIUS - DIRECTION_THRESHOLD:
            return None

        # Calculate angle
        angle = atan2(dy, dx)

        # Find the closest direction
        min_diff = float("inf")
        closest_direction = None

        for direction in self.DIRECTIONS:
            # Calculate angle difference (handling wrap-around)
            diff = abs(angle - direction.angle)
            diff = min(diff, 2 * pi - diff)

            if diff < min_diff:
                min_diff = diff
                closest_direction = direction

        return closest_direction

    def calculate_drag_distance(self, current_x: float, current_y: float) -> float:
        """Calculate the distance from drag start to current position"""
        dx = current_x - self.drag_start_x
        dy = current_y - self.drag_start_y
        return sqrt(dx * dx + dy * dy)

    def constrain_knob_position(self, x: float, y: float) -> tuple[float, float]:
        """Constrain the knob position to stay within the main circle"""
        dx = x - self.knob_center_x
        dy = y - self.knob_center_y
        distance = sqrt(dx * dx + dy * dy)

        max_distance = KNOB_RADIUS - KNOB_CENTER_RADIUS - 10

        if distance > max_distance:
            # Normalize and scale to max distance
            dx = (dx / distance) * max_distance
            dy = (dy / distance) * max_distance
            x = self.knob_center_x + dx
            y = self.knob_center_y + dy

        return x, y

    def get_canvas_coordinates(self, event: object) -> tuple[float, float]:
        """Get coordinates relative to canvas, handling boundary cases and scaling"""
        rect = self.canvas.getBoundingClientRect()
        x = event.clientX - rect.left
        y = event.clientY - rect.top

        # Scale coordinates from CSS size to actual canvas size
        scale_x = CANVAS_SIZE / rect.width
        scale_y = CANVAS_SIZE / rect.height

        x = x * scale_x
        y = y * scale_y

        # Clamp coordinates to canvas boundaries
        x = max(0, min(x, CANVAS_SIZE))
        y = max(0, min(y, CANVAS_SIZE))

        return x, y

    def on_mouse_down(self, event: object) -> None:
        """Handle mouse down event"""
        self.is_mouse_down = True
        self.is_dragging = False

        x, y = self.get_canvas_coordinates(event)

        # Check if click is on the center knob
        knob_x = self.knob_center_x + self.knob_offset_x
        knob_y = self.knob_center_y + self.knob_offset_y
        dx = x - knob_x
        dy = y - knob_y
        distance = sqrt(dx * dx + dy * dy)

        if distance <= KNOB_CENTER_RADIUS:
            self.drag_start_x = x
            self.drag_start_y = y
            self.draw_knob()

    def on_mouse_move(self, event: object) -> None:
        """Handle mouse move event"""
        if not self.is_mouse_down:
            return

        x, y = self.get_canvas_coordinates(event)

        # Check if we've moved enough to start dragging
        if not self.is_dragging:
            distance = self.calculate_drag_distance(x, y)
            if distance >= MIN_DRAG_DISTANCE:
                self.is_dragging = True

        if self.is_dragging:
            # Check if mouse is outside canvas boundaries
            if not self.is_within_canvas(x, y):
                # Reset knob position immediately when dragged outside
                self.reset_knob_position()
                return

            # Update knob position
            constrained_x, constrained_y = self.constrain_knob_position(x, y)
            self.knob_offset_x = constrained_x - self.knob_center_x
            self.knob_offset_y = constrained_y - self.knob_center_y

            self.draw_knob()

    def on_mouse_up(self, event: object) -> None:
        """Handle mouse up event"""
        if not self.is_mouse_down:
            return

        x, y = self.get_canvas_coordinates(event)

        # Only process mouse up if within canvas boundaries
        if not self.is_within_canvas(x, y):
            # Reset knob position and state without recording direction
            self.reset_knob_position()
            self.is_mouse_down = False
            self.is_dragging = False
            return

        # Only record direction if we were dragging and moved enough distance
        if self.is_dragging:
            direction = self.get_direction_from_coords(x, y)
            if direction:
                self.sequence.append(direction.name)
                self.update_output()

        # Reset knob position
        self.reset_knob_position()

        self.is_mouse_down = False
        self.is_dragging = False

        # Send sequence if we have one
        if self.sequence and self.on_key_received is not None:
            sequence_str = ",".join(self.sequence)
            self.on_key_received(sequence_str.encode())

    def update_output(self) -> None:
        """Update the text area with current sequence"""
        if self.output_textarea:
            self.output_textarea.value = " → ".join(self.sequence)

    def add_event_listeners(self) -> None:
        """Add mouse event listeners to canvas"""
        add_event_listener(self.canvas, "mousedown", self.on_mouse_down)
        add_event_listener(self.canvas, "mouseup", self.on_mouse_up)
        add_event_listener(self.canvas, "mousemove", self.on_mouse_move)

    def is_within_canvas(self, x: float, y: float) -> bool:
        """Check if coordinates are within canvas boundaries"""
        return 0 <= x <= CANVAS_SIZE and 0 <= y <= CANVAS_SIZE

    def reset_knob_position(self) -> None:
        """Reset knob to center position"""
        self.knob_offset_x = 0
        self.knob_offset_y = 0
        self.draw_knob()

    async def on_remove_last(self, _event: object) -> None:
        """Remove the last recorded move"""
        if self.sequence:
            self.sequence.pop()
            self.update_output()
            if self.on_key_received is not None:
                sequence_str = ",".join(self.sequence)
                await self.on_key_received(sequence_str.encode())

    async def on_reset_all(self, _event: object) -> None:
        """Reset all recorded moves"""
        self.sequence.clear()
        self.update_output()
        if self.on_key_received is not None:
            await self.on_key_received(b"")
