from dataclasses import dataclass
from math import pi

from js import console

from cj12.methods import KeyReceiveCallback
from cj12.dom import add_event_listener, elem_by_id

COLOUR_THEME = "#00ff00"

@dataclass
class Node:
    x_coor: int
    y_coor: int
    connected: bool

class PatternLockMethod:

    byte = 0x05
    static_id = "pattern_lock"
    name = "Pattern Lock"
    description = "A pattern traced lock"

    on_key_received: KeyReceiveCallback | None = None

    dot_radius: int = 15
    lock_grid_length: int = 300
    dimension: int = 3 # n by n dots


    async def setup(self) -> None: 
        self.init()
        self.setup_event_listener()

    def init(self) -> None:
        self.node_list: list[Node] = []
        self.last_node: Node | None = None
        self.sequence: list[int] = []
        self.is_mouse_down: bool = False
        self.connected_nodes: list[list[Node]] = []

        self.canvas = elem_by_id("grid")
        self.canvas.width = self.canvas.height = self.lock_grid_length
        self.ctx = self.canvas.getContext("2d")

        self.generate_nodes()
        self.draw_pattern()

    def generate_nodes(self) -> None:
        """
        Generate all the dots
        """
        node_length = self.lock_grid_length / self.dimension
        for row in range(self.dimension):
            for col in range(self.dimension):
                self.node_list.append(
                    Node(int(col * node_length + node_length / 2), 
                         int(row * node_length + node_length / 2), 
                         False)
                    )

    def draw_pattern(self) -> None:
        """
        Draw the dots and lines
        """
        ctx = self.canvas.getContext("2d")
        ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)

        for node in self.node_list:
            ctx.beginPath()
            ctx.arc(node.x_coor, node.y_coor, self.dot_radius, 0, 2*pi)
            ctx.lineWidth = 0
            if node.connected:
                ctx.fillStyle = COLOUR_THEME
            else:
                ctx.fillStyle = "white"

            ctx.fill()
            ctx.stroke()

        self.draw_line()

    def draw_line(self) -> None:
        """
        Draw the lines for connected dots
        """
        ctx = self.ctx
        for node1, node2 in self.connected_nodes:
            ctx.beginPath()
            ctx.moveTo(node1.x_coor, node1.y_coor)
            ctx.lineTo(node2.x_coor, node2.y_coor)
            ctx.strokeStyle = COLOUR_THEME
            ctx.lineWidth = 2   
            ctx.stroke()
    
    def on_move(self, evt) -> None:
        if not self.is_mouse_down:
            return
        
        rect = self.canvas.getBoundingClientRect()

        if hasattr(evt, "touches") and evt.touches.length:
            current_x = evt.touches[0].clientX - rect.left
            current_y = evt.touches[0].clientY - rect.top
        else:
            current_x = evt.clientX - rect.left
            current_y = evt.clientY - rect.top

        node = self.get_node(current_x, current_y)

        if node and not node.connected:
            node.connected = True
            self.sequence.append(self.node_list.index(node))

            if self.last_node: # and self.last_node is not node:
                self.connected_nodes.append([self.last_node, node])
            
            self.last_node = node
            
        self.draw_pattern()

        if self.last_node:
            ctx = self.ctx
            ctx.beginPath()
            ctx.moveTo(self.last_node.x_coor, self.last_node.y_coor)
            ctx.lineTo(current_x, current_y)
            ctx.strokeStyle = COLOUR_THEME
            ctx.lineWidth = 2   
            ctx.stroke()
            

    def get_node(self, x: int, y: int) -> Node | None:
        """
        Get the node of a given x, y coordinate in the canvas
        """
        for node in self.node_list:
            if ((x - node.x_coor) ** 2 + (y - node.y_coor) ** 2) ** 0.5 <= self.dot_radius:
                return node

    def on_dimension_change(self, evt) -> None:
        self.dimension = 3 + int(evt.target.value)
        self.init()

    def setup_event_listener(self) -> None:
        """
        Register all the event listener in the canvas
        """
        def mouse_down(evt):
            self.is_mouse_down = True

            for node in self.node_list:
                node.connected = False

            self.connected_nodes.clear()
            self.last_node = None
            self.sequence.clear()

        async def mouse_up(evt):
            self.is_mouse_down = False
            self.draw_pattern()

            if self.on_key_received is not None:
                await self.on_key_received("".join(map(lambda x: str(x), self.sequence)).encode())
                
            # console.log("".join(map(lambda x: str(x), self.sequence)))
        
        self.dimension_selection = elem_by_id("dial-num")
        add_event_listener(self.canvas, "mousedown", mouse_down)
        add_event_listener(self.canvas, "mouseup", mouse_up)
        add_event_listener(self.canvas, "mousemove", self.on_move)
        add_event_listener(self.dimension_selection, "input", self.on_dimension_change)

