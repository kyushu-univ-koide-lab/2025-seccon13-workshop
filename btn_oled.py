# push button test program
import board
import busio
import adafruit_ssd1306
import digitalio
import time

i2c_sda = board.GP2
i2c_scl = board.GP3
btns = {
    "up": digitalio.DigitalInOut(board.GP7),
    "left": digitalio.DigitalInOut(board.GP6),
    "down": digitalio.DigitalInOut(board.GP5),
    "right": digitalio.DigitalInOut(board.GP4),
    "A": digitalio.DigitalInOut(board.GP15),
    "B": digitalio.DigitalInOut(board.GP14)
}
for btn in btns.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

i2c = busio.I2C(i2c_scl, i2c_sda)

display_width = 128
display_height = 64
display = adafruit_ssd1306.SSD1306_I2C(display_width, display_height, i2c)

display.fill(0)
display.text(" push", 80, 0, 1)
display.text("button", 80, 10, 1)
display.show()

btns_printed = {
    "up": False,
    "left": False,
    "down": False,
    "right": False,
    "A": False,
    "B": False
}
has_change = False
while True:
    for i, btn_color in enumerate([ "up", "left", "down", "right", "A", "B" ]):
        if (not btns[btn_color].value) and (not btns_printed[btn_color]):
            # button pushed but keyword not printed
            display.text(btn_color, 0, i*10, 1)
            btns_printed[btn_color] = True
            print(btn_color, "pressed")
            has_change = True

        elif btns[btn_color].value and btns_printed[btn_color]:
            # button not pushed anymore but keyword still printed
            display.fill_rect(0, i*10, 80, 10, 0)
            btns_printed[btn_color] = False
            print(btn_color, "released")
            has_change = True

    if has_change:
        display.show()
        has_change = False

    time.sleep(0.1)
