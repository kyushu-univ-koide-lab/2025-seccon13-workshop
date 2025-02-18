import board
import busio
import adafruit_ssd1306
import digitalio
import time

# Set up I2C connection
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda, frequency=1000000)

# Set up buttons
btns = {
    "p1_up": digitalio.DigitalInOut(board.GP7),
    "p1_down": digitalio.DigitalInOut(board.GP6),
    "p2_up": digitalio.DigitalInOut(board.GP5),
    "p2_down": digitalio.DigitalInOut(board.GP4)
}
for btn in btns.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# Set up display
display_width = 128
display_height = 64
display = adafruit_ssd1306.SSD1306_I2C(display_width, display_height, i2c)
display.fill(0)
display.show()

# Game variables
paddle_height = 10
paddle_width = 5
p1_y = (display_height - 20) // 2
p2_y = (display_height - 20) // 2
ball_x = display_width // 2
ball_y = (display_height - 20) // 2 + 20
ball_dx = 1
ball_dy = 1
score1 = 0
score2 = 0

def update_display():
    display.fill(0)  # Clear display
    display.text(f"P1: {score1}", 5, 5, 1)
    display.text(f"P2: {score2}", display_width - 30, 5, 1)
    display.rect(0, 0, display_width, 20, 1)  # Draw game area
    display.fill_rect(ball_x, ball_y, 4, 4, 1)  # Draw ball
    display.fill_rect(0, p1_y, paddle_width, paddle_height, 1)  # Draw player 1 paddle
    display.fill_rect(display_width - paddle_width, p2_y, paddle_width, paddle_height, 1)  # Draw player 2 paddle
    display.show()

def check_collision():
    global ball_x, ball_y, ball_dx, ball_dy, score1, score2
    if ball_y <= 20 or ball_y >= display_height - 4:
        ball_dy *= -1
    if ball_x <= paddle_width and p1_y <= ball_y <= p1_y + paddle_height:
        ball_dx *= -1
    if ball_x >= display_width - paddle_width - 4 and p2_y <= ball_y <= p2_y + paddle_height:
        ball_dx *= -1
    if ball_x < 0:
        score2 += 1
        reset_ball()
    if ball_x > display_width:
        score1 += 1
        reset_ball()

def reset_ball():
    global ball_x, ball_y
    ball_x = display_width // 2
    ball_y = (display_height - 20) // 2 + 20

# Main game loop
while True:
    if not btns["p1_up"].value:
        p1_y = max(20, p1_y - 1)
    if not btns["p1_down"].value:
        p1_y = min(display_height - paddle_height, p1_y + 1)
    if not btns["p2_up"].value:
        p2_y = max(20, p2_y - 1)
    if not btns["p2_down"].value:
        p2_y = min(display_height - paddle_height, p2_y + 1)

    ball_x += ball_dx
    ball_y += ball_dy
    check_collision()
    update_display()
    time.sleep(0.008)
