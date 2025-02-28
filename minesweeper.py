import board
import busio
import adafruit_ssd1306
import digitalio
import time
import random

# I2C接続の設定
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda, frequency=1000000)

# ボタン設定（6つ）
btns = {
    "up": digitalio.DigitalInOut(board.GP7),     # 上移動
    "left": digitalio.DigitalInOut(board.GP6),   # 左移動
    "down": digitalio.DigitalInOut(board.GP5),   # 下移動
    "right": digitalio.DigitalInOut(board.GP4),  # 右移動
    "open": digitalio.DigitalInOut(board.GP14),  # マスを開く
    "mark": digitalio.DigitalInOut(board.GP15)   # マークをつける
}
for btn in btns.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# ディスプレイ設定
display_width = 128
display_height = 64
display = adafruit_ssd1306.SSD1306_I2C(display_width, display_height, i2c)
display.fill(0)
display.show()

# ゲーム設定
GRID_WIDTH = 8      # 横8マス
GRID_HEIGHT = 8     # 縦8マス
CELL_SIZE = 8       # 各マスの間隔
CELL_INNER = 7      # マスの実際のサイズ（7px）
CURSOR_SIZE = 8     # カーソルのあるマスは8px
NUM_MINES = 10      # 地雷の数

# UIの開始位置
UI_OFFSET_Y = 0

# ゲーム変数
cursor_x, cursor_y = 0, 0  # カーソル位置（初期値0）
board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
revealed = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
marked = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
game_over = False

# 地雷配置と各セルの数字計算
def place_mines():
    mines = set()
    while len(mines) < NUM_MINES:
        x, y = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
        if (x, y) not in mines:
            mines.add((x, y))
            board[y][x] = -1  # 地雷を -1 とする

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if board[y][x] == -1:
                continue
            count = sum(
                1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if (0 <= x+dx < GRID_WIDTH and 0 <= y+dy < GRID_HEIGHT and board[y+dy][x+dx] == -1)
            )
            board[y][x] = count

# 画面更新
def update_display():
    display.fill(0)

    # 各セル描画（画面全体を使う）
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            px, py = x * CELL_SIZE + 1, y * CELL_SIZE + UI_OFFSET_Y  # 隙間を作るための調整

            # カーソルのあるマスは少し大きくする
            if x == cursor_x and y == cursor_y:
                size = CURSOR_SIZE
                px, py = x * CELL_SIZE, y * CELL_SIZE + UI_OFFSET_Y  # カーソルは1px大きめ
            else:
                size = CELL_INNER

            # セルが開かれている場合（背景を黒にして数字を中央に表示）
            if revealed[y][x]:
                display.fill_rect(px, py, size-1, size-1, 0)
                text_x = px + (size // 2) - 2  # 中央寄せ
                text_y = py + (size // 2) - 3  # 中央寄せ
                if board[y][x] == -1:
                    display.text("*", text_x, text_y, 1)  # 地雷（中央）
                else:
                    display.text(str(board[y][x]), text_x, text_y, 1)  # 数字（中央）
            elif marked[y][x]:
                display.fill_rect(px, py, size-1, size-1, 1)
                text_x = px + (size // 2) - 2  # 中央寄せ
                text_y = py + (size // 2) - 4  # 中央寄せ
                display.text("o", text_x, text_y, 0)  # マーク付き（中央）
            else:
                display.fill_rect(px, py, size-1, size-1, 1)  # 未開封のマス

    # ゲームオーバー表示
    if game_over:
        display.text("GAME OVER", 70, 24, 1)  # 画面右中央に表示

    display.show()

# セルを開く
def reveal_cell(x, y):
    global game_over
    if revealed[y][x] or marked[y][x]:
        return
    revealed[y][x] = True
    if board[y][x] == -1:
        game_over = True

# マークのトグル
def toggle_mark(x, y):
    if revealed[y][x]:
        return
    marked[y][x] = not marked[y][x]

# 初期化
place_mines()
update_display()

# メインループ
while True:
    # 上ボタン
    if not btns["up"].value:
        cursor_y = (cursor_y - 1) % GRID_HEIGHT  # 端に着いたらループ
        time.sleep(0.05)
    # 下ボタン
    if not btns["down"].value:
        cursor_y = (cursor_y + 1) % GRID_HEIGHT
        time.sleep(0.05)
    # 左ボタン
    if not btns["left"].value:
        cursor_x = (cursor_x - 1) % GRID_WIDTH
        time.sleep(0.05)
    # 右ボタン
    if not btns["right"].value:
        cursor_x = (cursor_x + 1) % GRID_WIDTH
        time.sleep(0.05)
    # マスを開くボタン
    if not btns["open"].value:
        reveal_cell(cursor_x, cursor_y)
        time.sleep(0.05)
    # マークボタン
    if not btns["mark"].value:
        toggle_mark(cursor_x, cursor_y)
        time.sleep(0.05)

    update_display()
    time.sleep(0.05)
