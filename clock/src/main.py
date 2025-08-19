import asyncio
from machine import Pin, time_pulse_us
import time
import sys
from screen import colors, display, touchscreen
import screen
import timecode
from mapping_utils import is_zero, is_one, is_mark, load_mapping

# Define the pin connected to the sensor/signal
input_pin = Pin(35, Pin.IN) # Assuming GPIO 23

# Initialize clock and signal variables
hours, minutes, seconds = 0, 0, 0
year, month, day = 2025, 1, 1
time_code = ['_'] * 60
display_code = ['_'] * 60

# Update display?
needs_update = False


# Draw clock screen
def draw_clock_screen():
    # this is way too slow to do every refresh
    # screen.clear_display(colors['black'])

    screen.draw_text8x8(10, 20, f"DATE : {year:04}-{month:02}-{day:02}", colors['white'])
    screen.draw_text8x8(10, 45, f"TIME : {hours:02}:{minutes:02}:{seconds:02}", colors['white'])

    # may need to update in smalle increments to keep speed up
    screen.draw_text8x8(10, 80, f"TIME CODE : 1234567890", colors['white'])
    screen.draw_text8x8(10, 95, f"    01-10 : {''.join(display_code[0:10])}", colors['white'])
    screen.draw_text8x8(10, 110, f"    11-20 : {''.join(display_code[10:20])}", colors['white'])
    screen.draw_text8x8(10, 125, f"    21-30 : {''.join(display_code[20:30])}", colors['white'])
    screen.draw_text8x8(10, 140, f"    31-40 : {''.join(display_code[30:40])}", colors['white'])
    screen.draw_text8x8(10, 155, f"    41-50 : {''.join(display_code[40:50])}", colors['white'])
    screen.draw_text8x8(10, 170, f"    51-60 : {''.join(display_code[50:60])}", colors['white'])

# Handle touchscreen press
def touchscreen_press(y, x): # swap since screen is inverted
    print(f"Touch: X = {x} | Y = {y}")

async def main_signal():
    ticks = 1
    frame_counter = 0
    bit = '_'
    last_bit = -1
    found_frame = False
    
    global display, touchscreen
    global needs_update, hours, minutes, seconds, year, month, day, time_code, display_code

    try:
        while True:

            # time.sleep_us(10)  # Sleep for 1 millisecond to reduce CPU usage
            
            if ticks % 60 == 0:
                print(f"Ticks: {ticks}")
                ticks = 0
            ticks += 1

            # Measure the duration of the high pulse on sensor_pin
            pulse_duration_us = time_pulse_us(input_pin, 1, 2500000)  # 2 second timeout

            if pulse_duration_us > 0:
                if is_mark(pulse_duration_us / 1000000):
                    bit = 'M'
                    print(f"[{ticks:02d}] Data[{frame_counter:02d}]: MARK ({pulse_duration_us} us)")
                elif is_one(pulse_duration_us / 1000000):
                    bit = '1'
                    print(f"[{ticks:02d}] Data[{frame_counter:02d}]: 1  ({pulse_duration_us} us)")
                elif is_zero(pulse_duration_us / 1000000):
                    bit = '0'
                    print(f"[{ticks:02d}] Data[{frame_counter:02d}]: 0  ({pulse_duration_us} us)")
                else:
                    print(f"[{ticks:02d}] Data[{frame_counter:02d}]: UNKNOWN SIGNAL ({pulse_duration_us} us)")
            elif pulse_duration_us == None:
                print(f"[{ticks:02d}] Timeout during pulse measurement (Nones).")
            elif pulse_duration_us == -1:
                print(f"[{ticks:02d}] Timeout during pulse measurement.")
            elif pulse_duration_us == -2:
                print(f"[{ticks:02d}] Timeout waiting for pulse start.")

            # catch the beginning of the data frame                
            if bit == 'M' and last_bit == 'M':
                print(f"Found MM data frame marker")
                # Grab the time code for the display
                display_code = time_code.copy()

                frame_counter = 0
                time_code = ['_'] * 60
                time_code[0] = 'M'
                time_code[59] = 'M'
                ticks = 0
                found_frame = True
    
                # Update the screen
                needs_update = True            

            time_code[frame_counter] = bit
            frame_counter = (frame_counter + 1) % 60
    
            if bit == 'M' and last_bit != 'M':
                print(f"Found M data frame marker")
                # Grab the time code for the display
                display_code = time_code.copy()    
                needs_update = True            
            
            last_bit = bit
            await asyncio.sleep(0.1)

    except Exception as e:
        print('Error occurred: ', e)
        sys.print_exception(e)
    except KeyboardInterrupt:
        print('Program interrupted by the user')
    finally:
        screen.backlight.off()
        screen.cleanup()

async def main_display():
    global display, touchscreen
    global needs_update, hours, minutes, seconds, year, month, day, time_code, display_code

    screen.init_screen(touchscreen_press)
    screen.clear_display(colors['black'])

    while True:
        if needs_update == True:
            print(f"Updating screen...")
            try:
                if '_' in display_code:
                    print(f"Data: {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02} {''.join(display_code)} (update/part)")
                else:
                    print(f"Data: {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02} {''.join(display_code)} (update)")
                    year_2d = timecode._decode_year(display_code[45:54])
                    doy = timecode._decode_day_of_year(display_code[20:34])
                    year, month, day = timecode._decode_date(year_2d, doy)
                    hours = timecode._decode_hour(display_code[11:19])
                    minutes = timecode._decode_minute(display_code[1:9])                                       
            except Exception as e:
                print(f"ERROR: Error updating date/time: {e}")

            # print(f"Time : {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}")
            
            print(f"Drawing screen...")
            
            draw_clock_screen()
            # screen.get_touch()
            needs_update = False
            
            
            # seconds = (seconds + 1) % 60
            # minutes = (minutes + 1) % 60
            # hours = (hours + 1) % 24
        else:
            try:
                if '_' in display_code:
                    print(f"Data: {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02} {''.join(display_code)} (!update/part)")
                else:
                    print(f"Data: {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02} {''.join(display_code)} (!update)")
                    year_2d = timecode._decode_year(display_code[45:54])
                    doy = timecode._decode_day_of_year(display_code[20:34])
                    year, month, day = timecode._decode_date(year_2d, doy)
                    hours = timecode._decode_hour(display_code[11:19])
                    minutes = timecode._decode_minute(display_code[1:9])
            except Exception as e:
                print(f"ERROR: Error update date/time: {e} (no update)")

            # print(f"Time : {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}")
            
        await asyncio.sleep(1.0)

async def main():
    asyncio.create_task(main_display())
    asyncio.create_task(main_signal())

if __name__ == "__main__":
    # main()
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely
