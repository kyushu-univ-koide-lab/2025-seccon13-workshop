import board
import busio
import adafruit_ssd1306
import digitalio
import time
import random

# I2C接続の設定
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda)

# ボタンの設定
btn_up = digitalio.DigitalInOut(board.GP7)
btn_up.direction = digitalio.Direction.INPUT
btn_up.pull = digitalio.Pull.UP

btn_down = digitalio.DigitalInOut(board.GP5)
btn_down.direction = digitalio.Direction.INPUT
btn_down.pull = digitalio.Pull.UP

btn_left = digitalio.DigitalInOut(board.GP6)
btn_left.direction = digitalio.Direction.INPUT
btn_left.pull = digitalio.Pull.UP

btn_right = digitalio.DigitalInOut(board.GP4)
btn_right.direction = digitalio.Direction.INPUT
btn_right.pull = digitalio.Pull.UP

# ディスプレイの設定
display_width = 128
display_height = 64
display = adafruit_ssd1306.SSD1306_I2C(display_width, display_height, i2c)
display.fill(0)
display.show()

# 変数の宣言
snake = []
direction = (0, 0)
speed = 0
food = (0, 0)
score = 0
game_over = False
reset_game = False

# ゲームの変数と初期設定
def init_game():
    global snake
    global direction
    global speed
    global food
    global score
    global game_over
    global reset_game

    snake = [(display_width // 2, display_height // 2)]
    direction = (0, -1)  # 初期方向は上
    speed = 0.001
    food = (random.randint(0, (display_width // 4) - 1) * 4,
            random.randint(5, (display_height // 4) - 1) * 4)
    score = 0
    game_over = False
    reset_game = False

def update_display():
    display.fill(0)  # 画面をクリア
    display.text(f"Score: {score}", 5, 5, 1)
    display.fill_rect(food[0], food[1], 4, 4, 1)  # エサ
    for segment in snake:
        display.fill_rect(segment[0], segment[1], 4, 4, 1)  # ヘビ
    display.show()

def move_snake():
    global food, score, game_over

    # 新しい頭の位置を計算
    new_x = snake[0][0] + direction[0] * 4
    new_y = snake[0][1] + direction[1] * 4

    # 壁にぶつかったらゲームオーバー
    if new_x < 0 or new_x >= display_width or new_y < 0 or new_y >= display_height:
        game_over = True
        return

    # 自分自身との衝突判定
    new_head = (new_x, new_y)
    if new_head in snake:
        game_over = True
        return

    # ヘビの頭を新しい位置に追加
    snake.insert(0, new_head)

    # スネークがエサを食べたか判定
    if new_head == food:
        score += 1
        # スネークの体にエサが重ならないように、新しいエサをランダムに配置
        while True:
            new_food_x = random.randint(0, (display_width // 4) - 1) * 4
            new_food_y = random.randint(5, (display_height // 4) - 1) * 4
            if (new_food_x, new_food_y) not in snake:
                food = (new_food_x, new_food_y)
                break
    else:
        snake.pop()

while 1:
    init_game()
    # メインゲームループ
    while not game_over:
        # ボタン入力の読み取り
        if not btn_up.value and direction != (0, 1):
            direction = (0, -1)
            print("1")
        elif not btn_down.value and direction != (0, -1):
            direction = (0, 1)
            print("2")
        elif not btn_left.value and direction != (1, 0):
            direction = (-1, 0)
            print("3")
        elif not btn_right.value and direction != (-1, 0):
            direction = (1, 0)
            print("4")
        
        move_snake()
        update_display()
        time.sleep(speed)

    # ゲームオーバー時の表示
    display.fill(0)
    display.text("Game Over", display_width // 2 - 40, display_height // 2 - 10, 1)
    display.text(f"Score: {score}", display_width // 2 - 20, display_height // 2 + 10, 1)
    display.show()
    
    while not reset_game:
        if not btn_up.value:
            print("reset")
            game_over = False
            reset_game = True