from collections.abc import Callable
from typing import Any

from js import Promise, window

from cj12.dom import add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback

SQUARE_SIZE = 44
PIECE_SCALE = 2.5
PIECE_BASE_OFFSET = 8
MOUSE_DEADZONE_RADIUS = 7


class ChessMethod:
    byte = 0x02
    static_id = "chess"
    name = "Chess"
    description = "A certain chess position"

    on_key_received: KeyReceiveCallback | None = None
    chessboard: list[list[str | None]]

    async def setup(self) -> None:
        self.chesspieces = None
        self.chessboard = [[None] * 8 for _ in range(8)]
        self.dragging = None
        self.last_mousedown = None

        self.canvas_board: Any = elem_by_id("background-canvas")
        self.canvas_pieces: Any = elem_by_id("piece-canvas")

        self.ctx_board = self.canvas_board.getContext("2d")
        self.ctx_board.translate(
            self.canvas_board.width / 2,
            self.canvas_board.height / 2,
        )
        self.ctx_board.imageSmoothingEnabled = False

        self.ctx_pieces = self.canvas_pieces.getContext("2d")
        self.ctx_pieces.imageSmoothingEnabled = False
        self.ctx_pieces.translate(
            self.canvas_pieces.width / 2,
            self.canvas_pieces.height / 2,
        )

        add_event_listener(self.canvas_pieces, "mousedown", self.on_mouse_down)
        add_event_listener(self.canvas_pieces, "mouseup", self.on_mouse_up)
        add_event_listener(self.canvas_pieces, "mousemove", self.on_mouse_move)
        # add_event_listener(self.canvas_pieces, "dblclick", self.on_double_click)

        # Control buttons and handlers
        self.btn_clear: Any = elem_by_id("btn-clear-board")
        self.btn_initial: Any = elem_by_id("btn-initial-position")
        add_event_listener(self.btn_clear, "click", self.on_clear_board)
        add_event_listener(self.btn_initial, "click", self.on_initial_position)
        await self.load_chesspieces()

        # Draw the initial board
        self.draw_board()
        # Start with the standard initial position for convenience
        self.set_initial_position()
        self.draw_pieces_on_board(0, 0)
        await self.update_key()


    async def load_chesspieces(self) -> None:
        def load_image(src: str) -> object:
            def executor(
                resolve: Callable[[object], None],
                _reject: Callable[[object], None],
            ) -> None:
                img = window.Image.new()  # pyright: ignore[reportAttributeAccessIssue]
                img.onload = lambda *_, img=img: resolve(img)
                img.src = src

            return Promise.new(executor)  # pyright: ignore[reportAttributeAccessIssue]

        piece_names = [
            f"{color}_{piece}"
            for piece in ("King", "Queen", "Rook", "Bishop", "Knight", "Pawn")
            for color in "BW"
        ]
        images = await Promise.all(  # pyright: ignore[reportAttributeAccessIssue]
            [
                load_image(f"/methods/chess/pieces/{piece_name}.png")
                for piece_name in piece_names
            ],
        )
        self.chesspieces = dict(zip(piece_names, images, strict=False))
        self.piece_width = images[0].width * PIECE_SCALE
        self.piece_height = images[0].height * PIECE_SCALE


    # --- Controls ---
    def clear_board(self) -> None:
        self.chessboard = [[None] * 8 for _ in range(8)]
        self.dragging = None
        # Redraw pieces layer cleared
        self.ctx_pieces.clearRect(
            -self.canvas_pieces.width / 2,
            -self.canvas_pieces.height / 2,
            self.canvas_pieces.width,
            self.canvas_pieces.height,
        )
        self.draw_pieces_on_board(0, 0)

    async def on_clear_board(self, _event: object) -> None:
        self.clear_board()
        await self.update_key()

    def set_initial_position(self) -> None:
        # Use the piece names already loaded in pickzones/chesspieces.
        # Expected: W_King, W_Queen, W_Rook, W_Bishop, W_Knight, W_Pawn
        # Board indices: row 0 at top (black side), row 7 at bottom (white side)
        w = {
            "K": "W_King",
            "Q": "W_Queen",
            "R": "W_Rook",
            "B": "W_Bishop",
            "N": "W_Knight",
            "P": "W_Pawn",
        }
        b = {
            "K": "B_King",
            "Q": "B_Queen",
            "R": "B_Rook",
            "B": "B_Bishop",
            "N": "B_Knight",
            "P": "B_Pawn",
        }
        self.chessboard = [[None] * 8 for _ in range(8)]
        # Black back rank (row 0)
        for c, pc in enumerate(("R", "N", "B", "Q", "K", "B", "N", "R")):
            self.chessboard[0][c] = b[pc]
        # Black pawns (row 1)
        for c in range(8):
            self.chessboard[1][c] = b["P"]
        # Empty rows 2..5 already None
        # White pawns (row 6)
        for c in range(8):
            self.chessboard[6][c] = w["P"]
        # White back rank (row 7)
        for c, pc in enumerate(("R", "N", "B", "Q", "K", "B", "N", "R")):
            self.chessboard[7][c] = w[pc]

    async def on_initial_position(self, _event: object) -> None:
        self.set_initial_position()
        # Redraw
        self.draw_pieces_on_board(0, 0)
        await self.update_key()

    def draw_board(self) -> None:
        if self.chesspieces is None:
            return
        ctx, ssz = self.ctx_board, SQUARE_SIZE
        # ctx.strokeStyle = "#008800"
        # ctx.strokeRect(-board.width / 2, -board.height / 2, board.width, board.height)
        ctx.fillStyle = "#FBDEBD"
        ctx.fillRect(-4 * ssz - 5, -4 * ssz - 5, 8 * ssz + 10, 8 * ssz + 10)
        ctx.clearRect(-4 * ssz - 2, -4 * ssz - 2, 8 * ssz + 4, 8 * ssz + 4)
        ctx.fillRect(-4 * ssz, -4 * ssz, 8 * ssz, 8 * ssz)
        ctx.fillStyle = "#603814"
        for x in range(-4, 4):
            for y in range(-4 + (x % 2 == 0), 4, 2):
                ctx.fillRect(x * ssz, y * ssz, ssz, ssz)
        self.pickzones = {}
        piece_names = iter(self.chesspieces)
        for row in (-1, 0, 1):
            y = row * (self.piece_height + 1)
            for col in (0, 1):
                x = 4 * ssz + 10 + self.piece_width / 2 + col * (self.piece_width + 5)
                for xx in -x, x:
                    self.pickzones[piece := next(piece_names)] = (xx, y)
                    self.draw_piece(
                        piece,
                        xx,
                        y,
                        (-self.piece_width / 2, -self.piece_height / 2),
                        ctx,
                    )

    def draw_piece(
        self,
        piece_name: str,
        x: float,
        y: float,
        offset: tuple[float, float] | None = None,
        ctx: object | None = None,
    ) -> None:  # default anchor point is the center of the bottom edge
        if self.chesspieces is None:
            return
        img = self.chesspieces[piece_name]
        dx, dy = (
            (-self.piece_width / 2, -self.piece_height) if offset is None else offset
        )
        (self.ctx_pieces if ctx is None else ctx).drawImage(  # pyright: ignore[reportAttributeAccessIssue]
            img,
            x + dx,
            y + dy,
            self.piece_width,
            self.piece_height,
        )

    def draw_pieces_on_board(self, mx: float, my: float) -> None:
        self.ctx_pieces.clearRect(
            -self.canvas_pieces.width / 2,
            -self.canvas_pieces.height / 2,
            self.canvas_pieces.width,
            self.canvas_pieces.height,
        )
        ssz = SQUARE_SIZE
        dragged_piece_drawn = self.dragging is None
        drag = self.dragging
        for r in range(8):
            piece_bottom_y = (r - 3) * ssz - PIECE_BASE_OFFSET
            if not dragged_piece_drawn and (drag is not None) and my < piece_bottom_y:
                self.draw_piece(drag, mx, my)
                dragged_piece_drawn = True
            for c in range(8):
                if (piece := self.chessboard[r][c]) is not None:
                    self.draw_piece(piece, (c - 3.5) * ssz, piece_bottom_y)
        if not dragged_piece_drawn and drag is not None:
            self.draw_piece(drag, mx, my)

    def get_mouse_coords(self, event: object) -> tuple[float, float]:
        rect = self.canvas_board.getBoundingClientRect()  # pyright: ignore[reportAttributeAccessIssue]
        mx = event.clientX - rect.left - rect.width // 2  # pyright: ignore[reportAttributeAccessIssue]
        my = event.clientY - rect.top - rect.height // 2  # pyright: ignore[reportAttributeAccessIssue]
        return mx, my

    def mouse_on_board_square(self, mx: float, my: float):  # noqa: ANN201
        r, c = map(lambda x: int(x // SQUARE_SIZE) + 4, (my, mx))  # noqa: C417
        return (r, c) if r in range(8) and c in range(8) else None

    async def on_mouse_down(self, event: object) -> None:
        mx, my = self.get_mouse_coords(event)
        if board_square := self.mouse_on_board_square(mx, my):
            r, c = board_square
            self.dragging, self.chessboard[r][c] = self.chessboard[r][c], self.dragging
            self.last_mousedown = mx, my
            await self.update_key()
        else:
            for piece in self.pickzones:
                if (
                    abs(mx - self.pickzones[piece][0]) < self.piece_width // 2
                    and abs(my - self.pickzones[piece][1]) < self.piece_height // 2
                ):
                    self.dragging = piece
                    self.last_mousedown = mx, my
                    break
            else:
                self.dragging = None
        self.draw_pieces_on_board(mx, my)

    def on_mouse_move(self, event: object) -> None:
        if not self.dragging:
            return
        mx, my = self.get_mouse_coords(event)
        self.draw_pieces_on_board(mx, my)

    async def on_mouse_up(self, event: object) -> None:
        mx, my = self.get_mouse_coords(event)
        px, py = self.last_mousedown  # pyright: ignore[reportGeneralTypeIssues]
        if (px - mx) ** 2 + (py - my) ** 2 > MOUSE_DEADZONE_RADIUS**2:  # noqa: SIM102
            if self.dragging is not None and (
                board_square := self.mouse_on_board_square(mx, my)
            ):
                r, c = board_square
                self.chessboard[r][c], self.dragging = self.dragging, self.chessboard[r][c]
                self.draw_pieces_on_board(mx, my)
                await self.update_key()


    async def on_double_click(self, event: object) -> None:
        mx, my = self.get_mouse_coords(event)

        if (board_square := self.mouse_on_board_square(mx, my)) is None:
            return

        r, c = board_square
        if self.chessboard[r][c] is None:
            return

        self.chessboard[r][c] = None
        self.draw_pieces_on_board(mx, my)
        await self.update_key()


    async def update_key(self) -> None:
        conversion = {
            None: 0,
            "W_King": 1,
            "W_Queen": 2,
            "W_Rook": 3,
            "W_Bishop": 4,
            "W_Knight": 5,
            "W_Pawn": 6,
            "B_King": 7,
            "B_Queen": 8,
            "B_Rook": 9,
            "B_Bishop": 10,
            "B_Knight": 11,
            "B_Pawn": 12
        }
        key = [conversion[piece] for row in self.chessboard for piece in row]
        # print(key)  # debug
        await self.on_key_received(bytes(key))
