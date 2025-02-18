import board
import busio
import adafruit_ssd1306
import digitalio
import time

i2c_sda = board.GP2
i2c_scl = board.GP3
btns = {
    "red": digitalio.DigitalInOut(board.GP7),
    "green": digitalio.DigitalInOut(board.GP6),
    "blue": digitalio.DigitalInOut(board.GP5),
    "white": digitalio.DigitalInOut(board.GP4)
}
for btn in btns.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

i2c = busio.I2C(i2c_scl, i2c_sda)

display_width = 128
display_height = 64
display = adafruit_ssd1306.SSD1306_I2C(display_width, display_height, i2c)

display.fill(0)
display.show()

btns_printed = {
    "red": False,
    "green": False,
    "blue": False,
    "white": False
}
has_change = False
while True:
    for i, btn_color in enumerate(["red", "green", "blue", "white"]):
        if (not btns[btn_color].value) and (not btns_printed[btn_color]):
            # button pushed but keyword not printed
            display.text(btn_color, 0, i*10, 1)
            btns_printed[btn_color] = True
            has_change = True

        elif btns[btn_color].value and btns_printed[btn_color]:
            # button not pushed anymore but keyword still printed
            display.fill_rect(0, i*10, display_width, 10, 0)
            btns_printed[btn_color] = False
            has_change = True

    if has_change:
        display.show()
        has_change = False

    print("white: ", btns["white"].value)
    time.sleep(0.1)
