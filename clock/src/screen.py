from machine import Pin, SPI, SDCard, ADC, idle
from ili9341 import Display, color565
from xpt2046 import Touch
import hardware


# Define colors directly
colors = {
    'white': color565(255, 255, 255),
    'black': color565(0, 0, 0),
    'red': color565(255, 0, 0),
    'green': color565(0, 255, 0),
    'blue': color565(0, 32, 255),
    'yellow': color565(255, 255, 0)
}

# Screen globals
display = None
touchscreen = None

backlight = Pin(hardware.BACKLIGHT_PIN, Pin.OUT)

# Function to set up display and touchscreen
def setup_display_and_touchscreen(display_spi, touchscreen_spi):
    display = Display(display_spi, dc=Pin(hardware.DISPLAY_DC_PIN), cs=Pin(hardware.DISPLAY_CS_PIN), 
                      rst=Pin(hardware.DISPLAY_RST_PIN), width=320, height=240, rotation=90, bgr=False)
    touchscreen = Touch(touchscreen_spi, cs=Pin(hardware.TOUCHSCREEN_CS_PIN), int_pin=Pin(hardware.TOUCHSCREEN_INT_PIN))
    return display, touchscreen

# Initialize touchscreen with interrupt handler
def init_touchscreen_with_interrupt(touchscreen_spi, handler):
    touchscreen = Touch(touchscreen_spi, cs=Pin(hardware.TOUCHSCREEN_CS_PIN), int_pin=Pin(hardware.TOUCHSCREEN_INT_PIN), int_handler=handler)
    return touchscreen


# Initialize display and touchscreen
def init_screen(touchscreen_handler):
    global display, touchscreen
    display_spi = SPI(1, baudrate=60000000, sck=Pin(hardware.DISPLAY_SCK_PIN), mosi=Pin(hardware.DISPLAY_MOSI_PIN))
    touchscreen_spi = SPI(2, baudrate=1000000, sck=Pin(hardware.TOUCHSCREEN_SCK_PIN), mosi=Pin(hardware.TOUCHSCREEN_MOSI_PIN), miso=Pin(hardware.TOUCHSCREEN_MISO_PIN))

    display = Display(display_spi, dc=Pin(hardware.DISPLAY_DC_PIN), cs=Pin(hardware.DISPLAY_CS_PIN), 
                      rst=Pin(hardware.DISPLAY_RST_PIN), width=320, height=240, rotation=90, bgr=False)
    touchscreen = Touch(touchscreen_spi, cs=Pin(hardware.TOUCHSCREEN_CS_PIN), int_pin=Pin(hardware.TOUCHSCREEN_INT_PIN))

    # Initialize touchscreen with interrupt handler
    touchscreen = init_touchscreen_with_interrupt(touchscreen_spi, touchscreen_handler)
    
    backlight_on()

# Draw text
def draw_text8x8(x, y, text, color):
    display.draw_text8x8(x, y, text, color)


# Get touch
def get_touch():
    touchscreen.get_touch()

# Cleanup display
def cleanup():
    display.cleanup()
    
# Backlight on
def backlight_on():
    backlight.on()

# Backlight off
def backlight_off():
    backlight.off()

# Clear display
def clear_display(color):
    display.clear(color)
