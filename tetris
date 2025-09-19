# Tetris for RP2040 + SSD1306 (128x64) / CircuitPython
# Field: 10x16 cells, cell size = 4px
# Controls (pull-up buttons):
#   p1_up (GP7)   : Rotate
#   p1_down (GP6) : Soft Drop
#   p2_up (GP5)   : Move Right (auto-repeat)
#   p2_down (GP4) : Move Left  (auto-repeat)

import board
import busio
import adafruit_ssd1306
import digitalio
import time
import random

# ---------- Hardware setup ----------
# I2C pins (same as your Pong example)
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda, frequency=1000000)

# Buttons (active low with pull-up)
btns = {
    "p1_up": digitalio.DigitalInOut(board.GP7),   # Rotate
    "p1_down": digitalio.DigitalInOut(board.GP5), # Soft drop
    "p2_up": digitalio.DigitalInOut(board.GP4),   # Right
    "p2_down": digitalio.DigitalInOut(board.GP6)  # Left
}
for b in btns.values():
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP

# Display
DISPLAY_W, DISPLAY_H = 128, 64
display = adafruit_ssd1306.SSD1306_I2C(DISPLAY_W, DISPLAY_H, i2c)
display.fill(0)
display.show()

# ---------- Game constants ----------
CELL = 4
COLS = 10
ROWS = 16
FIELD_X = 2                    # left margin (px)
FIELD_Y = 0                    # top (px)
FIELD_W = COLS * CELL          # 40 px
FIELD_H = ROWS * CELL          # 64 px

# UI positions (right panel)
PANEL_X = FIELD_X + FIELD_W + 4  # start of right side area
PANEL_W = DISPLAY_W - PANEL_X - 2

SCORE_SINGLE = 100
SCORE_DOUBLE = 300
SCORE_TRIPLE = 500
SCORE_TETRIS = 800
SCORE_SOFTDROP = 1             # per soft-drop row

LINES_PER_LEVEL = 10
GRAVITY_START = 0.60           # seconds per step at level 1
GRAVITY_MIN = 0.08
GRAVITY_STEP = 0.07            # speed up per level

MOVE_DAS = 0.20                # initial delay for left/right hold
MOVE_RR  = 0.08                # repeat rate while holding

# ---------- Tetromino definitions ----------
# Shapes as rotation states of (x, y) offsets from the piece origin
# Origin is the top-left of a notional 4x4 box; spawn uses these offsets.
TETROMINOES = {
    'I': [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(1,0),(1,1),(1,2),(1,3)]
    ],
    'O': [
        [(1,0),(2,0),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(2,1)]
    ],
    'T': [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)]
    ],
    'S': [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
        [(1,1),(2,1),(0,2),(1,2)],
        [(0,0),(0,1),(1,1),(1,2)]
    ],
    'Z': [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(1,2),(2,2)],
        [(1,0),(0,1),(1,1),(0,2)]
    ],
    'J': [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)]
    ],
    'L': [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)]
    ]
}
PIECE_TYPES = list(TETROMINOES.keys())

# ---------- Utilities ----------
def shuffle_in_place(seq):
    # Fisher–Yates
    for i in range(len(seq) - 1, 0, -1):
        j = random.randint(0, i)  # 0～i を含む
        seq[i], seq[j] = seq[j], seq[i]
        
def new_board():
    # 0 = empty, 1 = filled (monochrome)
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def piece_spawn_x(piece_type):
    # Center-ish spawn: origin x near middle
    return COLS // 2 - 2

def piece_spawn_y():
    return 0

def cells_of(piece_type, rot, x, y):
    return [(x + dx, y + dy) for (dx, dy) in TETROMINOES[piece_type][rot]]

def in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS

def collides(board, piece_type, rot, x, y):
    for (cx, cy) in cells_of(piece_type, rot, x, y):
        if not in_bounds(cx, cy):
            return True
        if board[cy][cx]:
            return True
    return False

def lock_piece(board, piece_type, rot, x, y):
    for (cx, cy) in cells_of(piece_type, rot, x, y):
        if 0 <= cy < ROWS and 0 <= cx < COLS:
            board[cy][cx] = 1

def clear_lines(board):
    cleared = 0
    new_rows = []
    for r in range(ROWS):
        if all(board[r][c] == 1 for c in range(COLS)):
            cleared += 1
        else:
            new_rows.append(board[r])
    while len(new_rows) < ROWS:
        new_rows.insert(0, [0]*COLS)
    for r in range(ROWS):
        board[r] = new_rows[r]
    return cleared

def gravity_interval_for_level(level):
    val = max(GRAVITY_MIN, GRAVITY_START - (level-1)*GRAVITY_STEP)
    return val

# Simple wall-kick: try rotate; if collision, try x-1 or x+1
def try_rotate(board, piece_type, rot, x, y, dir=1):
    new_rot = (rot + dir) % 4
    if not collides(board, piece_type, new_rot, x, y):
        return new_rot, x
    if not collides(board, piece_type, new_rot, x-1, y):
        return new_rot, x-1
    if not collides(board, piece_type, new_rot, x+1, y):
        return new_rot, x+1
    return rot, x

# ---------- Input handling ----------
class HoldRepeater:
    """ Auto-repeat handler for left/right movement """
    def __init__(self, digital_in, initial_delay=MOVE_DAS, repeat_delay=MOVE_RR):
        self.pin = digital_in
        self.initial = initial_delay
        self.repeat = repeat_delay
        self.last_state = True  # pull-up: True=not pressed
        self.next_time = 0.0
        self.phase = 'idle'     # 'idle', 'held_initial', 'held_repeat'

    def pressed_edge(self):
        now = time.monotonic()
        state = self.pin.value  # True=not pressed, False=pressed
        edge = (self.last_state and not state)
        self.last_state = state
        if edge:
            self.phase = 'held_initial'
            self.next_time = now + self.initial
            return True
        return False

    def held_tick(self):
        # returns True when it's time to repeat an action while button is held
        now = time.monotonic()
        if not self.pin.value:  # still pressed
            if self.phase == 'held_initial' and now >= self.next_time:
                self.phase = 'held_repeat'
                self.next_time = now + self.repeat
                return True
            elif self.phase == 'held_repeat' and now >= self.next_time:
                self.next_time = now + self.repeat
                return True
        else:
            self.phase = 'idle'
        return False

# Map controls
btn_rotate = btns["p1_up"]
btn_soft   = btns["p1_down"]
rep_right  = HoldRepeater(btns["p2_up"])
rep_left   = HoldRepeater(btns["p2_down"])

# For single-press detection on rotate & soft drop
last_rotate_state = True
last_soft_state = True

def rotate_pressed():
    global last_rotate_state
    cur = btn_rotate.value
    pressed = (last_rotate_state and not cur)
    last_rotate_state = cur
    return pressed

def soft_pressed():
    global last_soft_state
    cur = btn_soft.value
    pressed = (last_soft_state and not cur)
    last_soft_state = cur
    return pressed

# ---------- Drawing ----------
def draw_cell(px, py):
    # filled cell of 4x4
    display.fill_rect(px, py, CELL, CELL, 1)

def draw_board(board):
    # Field border
    display.rect(FIELD_X-1, FIELD_Y-1, FIELD_W+2, FIELD_H+2, 1)
    # Filled cells
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]:
                draw_cell(FIELD_X + c*CELL, FIELD_Y + r*CELL)

def draw_piece(piece_type, rot, x, y):
    for (cx, cy) in cells_of(piece_type, rot, x, y):
        if cy >= 0:
            draw_cell(FIELD_X + cx*CELL, FIELD_Y + cy*CELL)

def draw_panel(score, level, lines, next_piece):
    # Header
    display.text("TETRIS", PANEL_X, 0, 1)
    display.text(f"S:{score}", PANEL_X, 12, 1)
    display.text(f"L:{level}", PANEL_X, 22, 1)
    display.text(f"Ln:{lines}", PANEL_X, 32, 1)
    # Next
    display.text("NEXT", PANEL_X, 44, 1)
    # mini preview (scale ~3x3 area)
    if next_piece:
        # Draw next piece in a small 16x16 box
        box_x = PANEL_X
        box_y = 54
        display.rect(box_x-1, box_y-1, 18, 18, 1)
        # center roughly
        for (dx, dy) in TETROMINOES[next_piece][0]:
            nx = box_x + 2 + dx*3//2  # compact
            ny = box_y + 2 + dy*3//2
            display.pixel(nx, ny, 1)
            display.pixel(nx+1, ny, 1)
            display.pixel(nx, ny+1, 1)
            display.pixel(nx+1, ny+1, 1)

def render(board, piece_type, rot, x, y, score, level, lines, next_piece):
    display.fill(0)
    draw_board(board)
    draw_piece(piece_type, rot, x, y)
    draw_panel(score, level, lines, next_piece)
    display.show()

# ---------- Game state ----------
def new_piece(bag):
    # 7-bag generator
    if not bag:
        bag.extend(PIECE_TYPES)
        shuffle_in_place(bag)
    return bag.pop()

def game_over_screen(score):
    display.fill(0)
    display.text("GAME OVER", 20, 20, 1)
    display.text(f"Score:{score}", 20, 32, 1)
    display.text("Press ROTATE", 8, 48, 1)
    display.show()
    # wait for rotate press to restart
    global last_rotate_state
    while True:
        cur = btn_rotate.value
        if last_rotate_state and not cur:
            last_rotate_state = cur
            break
        last_rotate_state = cur
        time.sleep(0.02)

def tetris_game():
    board = new_board()
    score = 0
    lines_cleared_total = 0
    level = 1

    bag = []
    curr = new_piece(bag)
    nextp = new_piece(bag)
    rot = 0
    x = piece_spawn_x(curr)
    y = piece_spawn_y()

    if collides(board, curr, rot, x, y):
        game_over_screen(score)
        return

    last_gravity = time.monotonic()
    fall_interval = gravity_interval_for_level(level)

    # movement repeat timers are inside HoldRepeater
    # draw first frame
    render(board, curr, rot, x, y, score, level, lines_cleared_total, nextp)

    # Lock delay (very small & simple)
    LOCK_DELAY = 0.25
    lock_timer = None

    while True:
        now = time.monotonic()
        moved = False

        # ----- Inputs -----
        # Rotate (on press)
        if rotate_pressed():
            new_rot, new_x = try_rotate(board, curr, rot, x, y, dir=1)
            if (new_rot != rot) or (new_x != x):
                rot, x = new_rot, new_x
                moved = True
                lock_timer = None  # reset lock if rotated

        # Left/Right (edge and hold)
        if rep_left.pressed_edge() or rep_left.held_tick():
            if not collides(board, curr, rot, x-1, y):
                x -= 1
                moved = True
                lock_timer = None
        if rep_right.pressed_edge() or rep_right.held_tick():
            if not collides(board, curr, rot, x+1, y):
                x += 1
                moved = True
                lock_timer = None

        # Soft drop (held increases gravity; press also nudges one step)
        soft_held = not btn_soft.value
        if soft_pressed():
            # single nudge on edge
            if not collides(board, curr, rot, x, y+1):
                y += 1
                score += SCORE_SOFTDROP
                moved = True

        # gravity tick
        cur_interval = fall_interval * (0.25 if soft_held else 1.0)
        if now - last_gravity >= cur_interval:
            last_gravity = now
            if not collides(board, curr, rot, x, y+1):
                y += 1
                if soft_held:
                    score += SCORE_SOFTDROP
                moved = True
                # moving down cancels lock timer
                lock_timer = None
            else:
                # start lock timer if touching ground
                if lock_timer is None:
                    lock_timer = now
                elif now - lock_timer >= LOCK_DELAY:
                    # lock piece
                    lock_piece(board, curr, rot, x, y)
                    # line clear
                    cleared = clear_lines(board)
                    if cleared:
                        if cleared == 1:
                            score += SCORE_SINGLE
                        elif cleared == 2:
                            score += SCORE_DOUBLE
                        elif cleared == 3:
                            score += SCORE_TRIPLE
                        elif cleared == 4:
                            score += SCORE_TETRIS
                        lines_cleared_total += cleared
                        # level up
                        new_level = 1 + lines_cleared_total // LINES_PER_LEVEL
                        if new_level != level:
                            level = new_level
                            fall_interval = gravity_interval_for_level(level)
                    # next piece
                    curr = nextp
                    nextp = new_piece(bag)
                    rot = 0
                    x = piece_spawn_x(curr)
                    y = piece_spawn_y()
                    lock_timer = None
                    if collides(board, curr, rot, x, y):
                        # Game Over
                        render(board, curr, rot, x, y, score, level, lines_cleared_total, nextp=None)
                        game_over_screen(score)
                        return

        if moved:
            render(board, curr, rot, x, y, score, level, lines_cleared_total, nextp)

        time.sleep(0.01)

# ---------- Main loop (restartable) ----------
while True:
    tetris_game()
    # after game over, loop restarts a new game
