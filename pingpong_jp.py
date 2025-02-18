import board
import busio
import adafruit_ssd1306
import digitalio
import time

# I2C接続の設定
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda, frequency=1000000)

# ボタンの設定
ボタン = {
    "プレイヤー1_上": digitalio.DigitalInOut(board.GP7),
    "プレイヤー1_下": digitalio.DigitalInOut(board.GP6),
    "プレイヤー2_上": digitalio.DigitalInOut(board.GP5),
    "プレイヤー2_下": digitalio.DigitalInOut(board.GP4)
}
for btn in ボタン.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# ディスプレイの設定
ディスプレイの幅 = 128
ディスプレイの高さ = 64
ディスプレイ = adafruit_ssd1306.SSD1306_I2C(ディスプレイの幅, ディスプレイの高さ, i2c)
ディスプレイ.fill(0)
ディスプレイ.show()

# ゲームの変数
パドルの高さ = 10
パドルの幅 = 5
プレイヤー1_y = (ディスプレイの高さ - 20) // 2
プレイヤー2_y = (ディスプレイの高さ - 20) // 2
ボール_x = ディスプレイの幅 // 2
ボール_y = (ディスプレイの高さ - 20) // 2 + 20
ボール_dx = 1
ボール_dy = 1
スコア1 = 0
スコア2 = 0

def ディスプレイを更新():
    ディスプレイ.fill(0)  # ディスプレイをクリア
    ディスプレイ.text(f"P1: {スコア1}", 5, 5, 1)
    ディスプレイ.text(f"P2: {スコア2}", ディスプレイの幅 - 30, 5, 1)
    ディスプレイ.rect(0, 0, ディスプレイの幅, 20, 1)  # ゲームエリアを描画
    ディスプレイ.fill_rect(ボール_x, ボール_y, 4, 4, 1)  # ボールを描画
    ディスプレイ.fill_rect(0, プレイヤー1_y, パドルの幅, パドルの高さ, 1)  # プレイヤー1のパドルを描画
    ディスプレイ.fill_rect(ディスプレイの幅 - パドルの幅, プレイヤー2_y, パドルの幅, パドルの高さ, 1)  # プレイヤー2のパドルを描画
    ディスプレイ.show()

def 衝突をチェック():
    global ボール_x, ボール_y, ボール_dx, ボール_dy, スコア1, スコア2
    if ボール_y <= 20 or ボール_y >= ディスプレイの高さ - 4:
        ボール_dy *= -1
    if ボール_x <= パドルの幅 and プレイヤー1_y <= ボール_y <= プレイヤー1_y + パドルの高さ:
        ボール_dx *= -1
    if ボール_x >= ディスプレイの幅 - パドルの幅 - 4 and プレイヤー2_y <= ボール_y <= プレイヤー2_y + パドルの高さ:
        ボール_dx *= -1
    if ボール_x < 0:
        スコア2 += 1
        ボールをリセット()
    if ボール_x > ディスプレイの幅:
        スコア1 += 1
        ボールをリセット()

def ボールをリセット():
    global ボール_x, ボール_y
    ボール_x = ディスプレイの幅 // 2
    ボール_y = (ディスプレイの高さ - 20) // 2 + 20

# メインゲームループ
while True:
    if not ボタン["プレイヤー1_上"].value:
        プレイヤー1_y = max(20, プレイヤー1_y - 1)
    if not ボタン["プレイヤー1_下"].value:
        プレイヤー1_y = min(ディスプレイの高さ - パドルの高さ, プレイヤー1_y + 1)
    if not ボタン["プレイヤー2_上"].value:
        プレイヤー2_y = max(20, プレイヤー2_y - 1)
    if not ボタン["プレイヤー2_下"].value:
        プレイヤー2_y = min(ディスプレイの高さ - パドルの高さ, プレイヤー2_y + 1)

    ボール_x += ボール_dx
    ボール_y += ボール_dy
    衝突をチェック()
    ディスプレイを更新()
    time.sleep(0.008)