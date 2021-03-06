import tkinter as tk

NORMAL_SQUARE_COLOR = '#FFFB33'
AREA1_SQUARE_COLOR = '#F3BBF1'
AREA2_SQUARE_COLOR = '#7CFC00'

class Board:
    def __init__(self, size):
        self._view = tk.Frame()
        self._view.pack(fill=tk.BOTH, expand=1)
        self._size = size

        self._zone1 = [[0, self._size - 1], [0, self._size - 2], [0, self._size - 3],
                         [0, self._size - 4],
                         [1, self._size - 1], [1, self._size - 2], [1, self._size - 3],
                         [2, self._size - 1], [2, self._size - 2],
                         [3, self._size - 1]]
        self._zone2 = [[self._size - 1, 0], [self._size - 1, 1], [self._size - 1, 2],
                         [self._size - 1, 3],
                         [self._size - 2, 0], [self._size - 2, 1], [self._size - 2, 2],
                         [self._size - 3, 0], [self._size - 3, 1],
                         [self._size - 4, 0]]

        self._init_view()

    def _init_view(self):
        self._canvas = tk.Canvas(self._view, bg="#477D92")
        self._canvas.pack(fill=tk.BOTH, expand=1)

        self._grid = [[None] * self._size] * self._size
        self._player1 = []
        self._player1_pieces = []
        self._player2 = []
        self._player2_pieces = []

        for x in range(self._size):
            for y in range(self._size):
                BLACK = "#000"
                fill = tag = ""
                if x % 2 == 0:
                    if y % 2 == 0:
                        fill = BLACK
                        tag = "black"
                    else:
                        fill = NORMAL_SQUARE_COLOR
                        tag = "yellow"
                else:
                    if y % 2 == 0:
                        fill = NORMAL_SQUARE_COLOR
                        tag = "yellow"
                    else:
                        fill = BLACK
                        tag = "black"
                self._grid[x][y] = self._canvas.create_rectangle(x * 50 + 40, y * 50 + 30, x * 50 + 90, y * 50 + 80, outline="#fff", fill=fill, tags=tag)

        self._canvas.tag_bind("piece", "<ButtonPress-1>", self._onPressDown)
        self._canvas.tag_bind("piece", "<B1-Motion>", self._onMove)
        self._canvas.tag_bind("piece", "<ButtonRelease-1>", self._onPressUp)

    def _onPressDown(self, event):
        piece = self._canvas.find_closest(event.x, event.y)
        while "piece" not in self._canvas.gettags(piece):
            piece = self._canvas.find_closest(event.x, event.y, start=piece)
        self._dragged_piece = {"piece": piece, "x": event.x, "y": event.y }
        self._current_drag_pos = [self._dragged_piece["x"], self._dragged_piece["y"]]
        print(event.x)

    def _onMove(self, event):
        delta = [event.x - self._current_drag_pos[0], event.y - self._current_drag_pos[1]]
        self._canvas.move(self._dragged_piece["piece"], delta[0], delta[1])
        self._current_drag_pos = [event.x, event.y]

    def _onPressUp(self, event):
        self._dragged_piece = {}
        self._current_drag_pos = []

    def update(self, player1, player2):
        self._player1 = player1
        self._player2 = player2

        for piece in self._player1_pieces:
            self._canvas.delete(piece)
        for piece in self._player2_pieces:
            self._canvas.delete(piece)

        self._player1_pieces = [self._canvas.create_oval(x * 50 + 45, y * 50 + 35, x * 50 + 85, y * 50 + 75, fill="#BB578F",
                                                  tag=("piece", "player1")) for [x, y] in player1]
        self._player2_pieces = [self._canvas.create_oval(x * 50 + 45, y * 50 + 35, x * 50 + 85, y * 50 + 75, fill="#B2D965",
                                                  tag=("piece", "player1")) for [x, y] in player2]

    def _is_tile_empty(self, x, y):
        return [x, y] in self._player1 or [x, y] in self._player2

    def findLegalMoves(self, player):
        legalMoves = set()

        # first, we want to find all jump moves
        for i in range(self._size):
            for j in range(self._size):
                if self._is_tile_empty(i, j):
                    self.findJump([i, j], [i, j - 1], legalMoves)
                    self.findJump([i, j], [i, j + 1], legalMoves)
                    self.findJump([i, j], [i - 1, j], legalMoves)
                    self.findJump([i, j], [i - 1, j - 1], legalMoves)
                    self.findJump([i, j], [i - 1, j + 1], legalMoves)
                    self.findJump([i, j], [i + 1, j], legalMoves)
                    self.findJump([i, j], [i + 1, j - 1], legalMoves)
                    self.findJump([i, j], [i + 1, j + 1], legalMoves)

        # Find regular moves
        for i in range(self._size):
            for j in range(self._size):
                if self._is_tile_empty(i, j):
                    self.findRegularMove([i, j], legalMoves)

        return legalMoves

    def findJump(self, current, transit, legalMoves):
        if transit[0] < 0 or transit[0] >= self._size or transit[1] < 0 or transit[1] >= self._size:
            return

        for i in range(transit[0] - 1, transit[0] + 2):
            for j in range(transit[1] - 1, transit[1] + 2):
                if ((i - transit[0]) == (transit[0] - current[0]) and
                            (j - transit[1]) == (transit[1] - current[1]) and
                        (not (i == current[0] and j == current[1]))):
                    if self._is_tile_empty(i, j):
                        legalMoves.add([i, j])

    def findRegularMove(self, current, legalMoves):
        for i in range(current[0] - 1, current[0] + 2):
            for j in range(current[1] - 1, current[1] + 2):
                if self._is_tile_empty(i, j) and 0 <= i < self._size and 0 <= j < self._size and \
                        not(current[0] == i and current[1] == j):
                    legalMoves.add([i, j])

class Game:
    def __init__(self, size):
        self._size = size
        self.status = [] # will be set to status widget when created

        self._board = Board(size)
        self.player1 = self.zone1 = [[0, self._size - 1], [0, self._size - 2], [0, self._size - 3],
                         [0, self._size - 4],
                         [1, self._size - 1], [1, self._size - 2], [1, self._size - 3],
                         [2, self._size - 1], [2, self._size - 2],
                         [3, self._size - 1]]
        self.player2 = self.zone2 = [[self._size - 1, 0], [self._size - 1, 1], [self._size - 1, 2],
                         [self._size - 1, 3],
                         [self._size - 2, 0], [self._size - 2, 1], [self._size - 2, 2],
                         [self._size - 3, 0], [self._size - 3, 1],
                         [self._size - 4, 0]]
        self._board.update(self.player1, self.player2)

        self.player1[0] = [5, 5]
        self._board.update(self.player1, self.player2)


        all(piece in self.zone2 for piece in self.player1)
        all(piece in self.zone1 for piece in self.player2)

    def _add_reset_btn(self):
        # create a restart button to restart the game
        resetButton = tk.Button(text="RESTART", command=lambda: self.restart())
        resetButton.grid(row=self.boardSize+2, columnspan=self.boardSize)

    def _add_quit_btn(self):
        # create a quit button to quit the game
        quitButton = tk.Button(text="QUIT", command=lambda: self.quit())
        quitButton.grid(row=self.boardSize+4, columnspan=self.boardSize)

    def restart(self):
        self._board = Board(size)

    def move(self):
        #todo
        pass

    def winning(self):
        if all(piece in self.zone2 for piece in self.player1):
            displayStatus(mystatus, "Pink player aka player 1 wins!")
        if all(piece in self.zone1 for piece in self.player2):
            displayStatus(mystatus, "Green player aka player 2 wins!")
    
    def displayStatus(alabel, msg):
        alabel.config(bg='yellow', fg='red', text=msg)
        alabel.after(3000, lambda: theButton.config(image=newImage, text=newText))

if __name__ == "__main__":
    size = 8

    root = tk.Tk()
    root.wm_title("Halma {0:d} x {0:d}".format(size))
    game = Game(size)

    root.mainloop()
