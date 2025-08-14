from js import document, Image, Promise
from pyodide.ffi import create_proxy


class ChessboardLock:

    # Board settings
    SQUARE_SIZE = 44
    PIECE_SCALE = 2.5
    PIECE_BASE_OFFSET = 8

    def __init__(self):
        self.chesspieces = None
        self.chessboard = [[None] * 8 for _ in range(8)]
        self.dragging = None
        self.last_mousedown = None
        self.canvas_board = document.createElement("canvas")
        self.canvas_pieces = document.createElement("canvas")
        for elem, z in ((self.canvas_board, 0), (self.canvas_pieces, 1)):
            elem.width = 600
            elem.height = 400
            elem.style.position = "absolute"
            elem.style.left = "50%"
            elem.style.top = "50%"
            elem.style.transform = "translate(-50%, -50%)"
            elem.style.zIndex = z
            document.body.appendChild(elem)
        self.ctx_board = self.canvas_board.getContext("2d")
        self.ctx_board.translate(self.canvas_board.width / 2, self.canvas_board.height / 2)
        self.ctx_board.imageSmoothingEnabled = False
        self.ctx_pieces = self.canvas_pieces.getContext("2d")
        self.ctx_pieces.imageSmoothingEnabled = False
        self.ctx_pieces.translate(self.canvas_pieces.width / 2, self.canvas_pieces.height / 2)
        for event, proxy in (("mousedown", self.on_mouse_down), ("mousemove", self.on_mouse_move), ("mouseup", self.on_mouse_up)):
            self.canvas_pieces.addEventListener(event, create_proxy(proxy))


    @staticmethod
    async def init():
        instance = ChessboardLock()
        await instance.load_chesspieces()
        instance.draw_board()
        return instance


    async def load_chesspieces(self) -> None:
        def load_image(src):
            def executor(resolve, reject):
                img = Image.new()
                img.onload = lambda *_: resolve(img)
                img.src = src
            return Promise.new(executor)
        piece_names = [f"{color}_{piece}" for piece in ("King", "Queen", "Rook", "Bishop", "Knight", "Pawn") for color in "BW"]
        images = await Promise.all([load_image(f"cj12/assets/16x32 pieces/{piece_name}.png") for piece_name in piece_names])
        self.chesspieces = dict(zip(piece_names, images))
        for piece, img in self.chesspieces.items():
            print(f"{piece}: ({img.height}, {img.width})")
        self.piece_width = images[0].width * ChessboardLock.PIECE_SCALE
        self.piece_height = images[0].height * ChessboardLock.PIECE_SCALE


    def draw_board(self):
        board, ctx, SSZ = self.canvas_board, self.ctx_board, ChessboardLock.SQUARE_SIZE
        ctx.strokeStyle = "#008800"
        ctx.strokeRect(-board.width / 2, -board.height / 2, board.width, board.height)
        ctx.fillStyle = "#FBDEBD"
        ctx.fillRect(-4 * SSZ - 5, -4 * SSZ - 5, 8 * SSZ + 10, 8 * SSZ + 10)
        ctx.clearRect(-4 * SSZ - 2, -4 * SSZ - 2, 8 * SSZ + 4, 8 * SSZ + 4)
        ctx.fillRect(-4 * SSZ, -4 * SSZ, 8 * SSZ, 8 * SSZ)
        ctx.fillStyle = "#603814"
        for x in range(-4, 4):
            for y in range(-4 + (x % 2 == 0), 4, 2):
                ctx.fillRect(x * SSZ, y * SSZ, SSZ, SSZ)
        self.pickzones = {}
        piece_names = iter(self.chesspieces)
        for row in (-1, 0, 1):
            y = row * (self.piece_height + 1)
            for col in (0, 1):
                x = 4 * SSZ + 10 + self.piece_width / 2 + col * (self.piece_width + 5)
                for xx in -x, x:
                    self.pickzones[piece := next(piece_names)] = (xx, y)
                    self.draw_piece(piece, xx, y, (-self.piece_width / 2, -self.piece_height / 2), ctx)


    def draw_piece(self, piece_name, x, y, offset=None, ctx=None):  # default anchor point is the center of the bottom edge
        img = self.chesspieces[piece_name]
        dx, dy = (-self.piece_width / 2, -self.piece_height) if offset is None else offset
        (self.ctx_pieces if ctx is None else ctx).drawImage(img, x + dx, y + dy, self.piece_width, self.piece_height)


    def draw_pieces_on_board(self, mx, my):
        self.ctx_pieces.clearRect(-self.canvas_pieces.width / 2, -self.canvas_pieces.height / 2, self.canvas_pieces.width, self.canvas_pieces.height)
        SSZ = ChessboardLock.SQUARE_SIZE
        dragged_piece_drawn = self.dragging is None
        for r in range(8):
            piece_bottom_y = (r - 3) * SSZ - ChessboardLock.PIECE_BASE_OFFSET
            if not dragged_piece_drawn and my < piece_bottom_y:
                self.draw_piece(self.dragging, mx, my)
                dragged_piece_drawn = True
            for c in range(8):
                if (piece := self.chessboard[r][c]) is not None:
                    self.draw_piece(piece, (c - 3.5) * SSZ, piece_bottom_y)
        if not dragged_piece_drawn:
            self.draw_piece(self.dragging, mx, my)


    def get_mouse_coords(self, event):
        rect = self.canvas_board.getBoundingClientRect()
        mx = event.clientX - rect.left - rect.width // 2 
        my = event.clientY - rect.top - rect.height // 2
        return mx, my


    def mouse_on_board_square(self, mx, my):
        r, c = map(lambda x: int(x // ChessboardLock.SQUARE_SIZE) + 4, (my, mx))
        return (r, c) if r in range(8) and c in range(8) else None


    def on_mouse_down(self, event):
        mx, my = self.get_mouse_coords(event)
        if board_square := self.mouse_on_board_square(mx, my):
            r, c = board_square
            print(f"Clicked square: ({r}, {c})")
            self.dragging, self.chessboard[r][c] = self.chessboard[r][c], self.dragging
            self.last_mousedown = mx, my
        else:
            for piece in self.pickzones:
                if abs(mx - self.pickzones[piece][0]) < self.piece_width // 2 and abs(my - self.pickzones[piece][1]) < self.piece_height // 2:
                    print(f"Clicked piece: {piece}")
                    self.dragging = piece
                    self.last_mousedown = mx, my
                    break
            else:
                self.dragging = None
        self.draw_pieces_on_board(mx, my)


    def on_mouse_move(self, event):
        if not self.dragging:
            return
        mx, my = self.get_mouse_coords(event)
        self.draw_pieces_on_board(mx, my)


    def on_mouse_up(self, event):
        mx, my = self.get_mouse_coords(event)
        if self.last_mousedown != (mx, my):
            if self.dragging and (board_square := self.mouse_on_board_square(mx, my)):
                r, c = board_square
                self.chessboard[r][c] = self.dragging
                self.dragging = None
                self.draw_pieces_on_board(mx, my)