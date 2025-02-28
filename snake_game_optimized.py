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

    display.fill(0)
    display.show()

    snake = [(display_width // 2, display_height // 2)]
    direction = (0, -1)  # 初期方向は上
    speed = 0.001
    food = (random.randint(0, (display_width // 4) - 1) * 4,
            random.randint(5, (display_height // 4) - 1) * 4)
    display.fill_rect(food[0], food[1], 4, 4, 1)
    score = 0
    update_score()
    game_over = False
    reset_game = False

def update_score():
    # スコアの背景を消去
    display.fill_rect(0, 0, display_width, 10, 0)  # 上部10pxをクリア

    # スコアを再描画
    display.text(f"Score: {score}", 5, 5, 1)

    # 画面更新
    display.show()

def move_snake():
    global food, score, game_over

    # 現在のスネークの頭の位置
    old_head = snake[0]
    
    # 新しい頭の位置を計算
    new_x = old_head[0] + direction[0] * 4
    new_y = old_head[1] + direction[1] * 4
    new_head = (new_x, new_y)

    # 壁にぶつかったらゲームオーバー
    if new_x < 0 or new_x >= display_width or new_y < 0 or new_y >= display_height:
        game_over = True
        return

    # 自分自身との衝突判定
    if new_head in snake:
        game_over = True
        return

    # 新しい頭をリストに追加
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

        update_score()
    else:
        # しっぽを削除し、そこだけ消去
        tail = snake.pop()
        display.fill_rect(tail[0], tail[1], 4, 4, 0)  # しっぽ部分を黒で消す

    display.fill_rect(new_head[0], new_head[1], 4, 4, 1)  # 頭を描画
    display.fill_rect(food[0], food[1], 4, 4, 1)  # エサを再描画

    # 画面更新
    display.show()


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