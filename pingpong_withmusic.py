import board
import busio
import adafruit_ssd1306
import digitalio
import time
import asyncio
import audiocore
import audiopwmio
import array
import math

# Set up I2C connection
i2c_sda = board.GP2
i2c_scl = board.GP3
i2c = busio.I2C(i2c_scl, i2c_sda, frequency=1000000)

# Set up buttons
btns = {
    "p1_up": digitalio.DigitalInOut(board.GP7),
    "p1_down": digitalio.DigitalInOut(board.GP6),
    "p2_up": digitalio.DigitalInOut(board.GP4),
    "p2_down": digitalio.DigitalInOut(board.GP5)
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
ball_size = 4
p1_y = (display_height - 20) // 2 + 20
p2_y = (display_height - 20) // 2 + 20
ball_x = display_width // 2
ball_y = (display_height - 20) // 2 + 20
ball_dx = 1
ball_dy = 1
score1 = 0
score2 = 0

# Speaker setup
speaker = audiopwmio.PWMAudioOut(board.GP12)

def generate_sine_wave(frequency, sample_rate=8000, duration=1):
    length = sample_rate // frequency
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int(math.sin(2 * math.pi * i / length) * 32767 + 32767)
    sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)
    return sample

async def play_music():
    sample = generate_sine_wave(440)
    speaker.play(sample, loop=True)
    await asyncio.sleep(1)
    speaker.stop()

def init_board():
    display.fill(0)
    display.text(f"P1: {score1}", 5, 5, 1)
    display.text(f"P2: {score2}", display_width - 31, 5, 1)
    display.rect(0, 0, display_width, 20, 1)  # Draw game area
    display.fill_rect(0, p1_y, paddle_width, paddle_height, 1)  # Draw player 1 paddle
    display.fill_rect(display_width - paddle_width, p2_y, paddle_width, paddle_height, 1)  # Draw player 2 paddle

def update_ball():
    global ball_x, ball_y, ball_dx, ball_dy, score1, score2
    display.fill_rect(ball_x, ball_y, ball_size, ball_size, 0)  # Remove ball

    # Progress one frame
    ball_x += ball_dx
    ball_y += ball_dy

    # Update scores if needed
    if ball_x < paddle_width:
        score2 += 1
        asyncio.create_task(play_music())
        reset_ball()
    elif ball_x > display_width - paddle_width - ball_size:
        score1 += 1
        asyncio.create_task(play_music())
        reset_ball()
    else:
        # Flip the speed if needed
        if ball_y <= 20 or ball_y >= display_height - ball_size:
            ball_dy *= -1

        if ball_x <= paddle_width and p1_y - ball_size <= ball_y <= p1_y + paddle_height:
            ball_dx *= -1
        elif ball_x >= display_width - paddle_width - ball_size and p2_y - ball_size <= ball_y <= p2_y + paddle_height:
            ball_dx *= -1

    display.fill_rect(ball_x, ball_y, ball_size, ball_size, 1)  # Draw ball
    display.show()

def reset_ball():
    global ball_x, ball_y
    ball_x = display_width // 2
    ball_y = (display_height - 20) // 2 + 20

    display.fill_rect(1, 1, display_width-2, 20-2, 0)  # Remove texts
    display.text(f"P1: {score1}", 5, 5, 1)
    display.text(f"P2: {score2}", display_width - 32, 5, 1)

async def game_loop():
    global p1_y, p2_y
    init_board()
    while True:
        if not btns["p1_up"].value:
            old_p1_y = p1_y
            p1_y = max(20, p1_y - 1)
            if old_p1_y != p1_y:
                display.fill_rect(0, p1_y, paddle_width, 1, 1)
                display.fill_rect(0, p1_y + paddle_height, paddle_width, 1, 0)
        elif not btns["p1_down"].value:
            old_p1_y = p1_y
            p1_y = min(display_height - paddle_height, p1_y + 1)
            if old_p1_y != p1_y:
                display.fill_rect(0, old_p1_y, paddle_width, 1, 0)
                display.fill_rect(0, old_p1_y + paddle_height, paddle_width, 1, 1)

        if not btns["p2_up"].value:
            old_p2_y = p2_y
            p2_y = max(20, p2_y - 1)
            if old_p2_y != p2_y:
                display.fill_rect(display_width - paddle_width, p2_y, paddle_width, 1, 1)
                display.fill_rect(display_width - paddle_width, p2_y + paddle_height, paddle_width, 1, 0)
        elif not btns["p2_down"].value:
            old_p2_y = p2_y
            p2_y = min(display_height - paddle_height, p2_y + 1)
            if old_p2_y != p2_y:
                display.fill_rect(display_width - paddle_width, old_p2_y, paddle_width, 1, 0)
                display.fill_rect(display_width - paddle_width, old_p2_y + paddle_height, paddle_width, 1, 1)

        update_ball()
        await asyncio.sleep(0.008)

# Run the main async loop
asyncio.run(game_loop())