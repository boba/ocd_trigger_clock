from machine import Pin, UART, PWM
import time
import utime
from micropyGPS import MicropyGPS
from timecode import create_timecode
from mapping_utils import load_mapping, zero, one, mark


SPACE_DURATION = int(0.01 * 1000000) # Space duration in microseconds

# Initialize the pin as an output pin.
output_pin = Pin(16, Pin.OUT)
output_pin.value(0)  # Set the pin to low initially.

# setup GPIO pins 6 TX and 7 RX as UART 2 for GPS serial
gps_serial = UART(2, baudrate=9600, tx=Pin(6), rx=Pin(7))

# setup GPIO pin 18 as a PWM pin for servo control
servo = PWM(Pin(18, mode=Pin.OUT))  # Initialize PWM on pin 18 for servo control
servo.freq(50)  # Set frequency to 50Hz for servo control
TICK_POS = 25
TOCK_POS = 55
servo.duty(int((TOCK_POS - TICK_POS) / 2))
servo_position = TOCK_POS

# Initialize MicropyGPS instance
gps = MicropyGPS()

# def get_zero():
#     return int(0.70 * 1000000)  # 0.5 seconds in microseconds

# def get_one():
#     return int(1.499 * 1000000)  # 1.5 seconds in microseconds

# def get_mark():
#     return int(0.49 * 1000000)  # 0.51 seconds in microseconds

def flip_servo(quiet=True):
    global servo, servo_position
    if not quiet:
        if servo_position == TICK_POS:
            servo.duty(TOCK_POS)
            servo_position = TOCK_POS
        else:
            servo.duty(TICK_POS)
            servo_position = TICK_POS

def send_bit(val, dur, quiet=True):
    """Send a single bit with the specified duration."""
    print(f"Sending {val}: {dur} us")
    flip_servo(quiet)
    output_pin.value(1)  
    utime.sleep_us(int(dur * 1000000) )  
    output_pin.value(0)
    utime.sleep_us(SPACE_DURATION)  # Add a small space after sending zero

# def send_zeroes(qty, quiet=True):
#         xdur = get_zero()
#         dur = zero()
#         print("Sending 0: {dur} us {xdur}".format(dur=dur, xdur=xdur))
#         flip_servo(quiet)
#         output_pin.value(1)  
#         utime.sleep_us(int(dur * 1000000) )  
#         output_pin.value(0)
#         utime.sleep_us(SPACE_DURATION)  # Add a small space after sending zero

# def send_ones(qty, quiet=True):
#     for _ in range(qty):
#         xdur = get_one()
#         dur = one()
#         print("Sending 1: {dur} us {xdur}".format(dur=dur, xdur=xdur))
#         flip_servo(quiet)
#         output_pin.value(1)  
#         utime.sleep_us(int(dur * 1000000) )  
#         output_pin.value(0)
#         utime.sleep_us(SPACE_DURATION) # Add a small space after sending one
        
# def send_marks(qty, quiet=True):
#     for _ in range(qty):
#         xdur = get_mark()
#         dur = mark()
#         print("Sending MARK: {dur} us {xdur}".format(dur=dur, xdur=xdur))
#         flip_servo(quiet)
#         output_pin.value(1)  
#         utime.sleep_us(int(dur * 1000000) )  
#         output_pin.value(0)
#         utime.sleep_us(SPACE_DURATION)  # Add a small space after sending mark

def dump_gps_data():
    print(f"Satellite Data:")
    print(f"    In Use: {gps.satellites_in_use}, Visible: {gps.satellites_visible()},  Used: {gps.satellites_used}")
    print(f"    Fix: {gps.fix_type}, HDOP: {gps.hdop}, VDOP: {gps.vdop}, PDOP: {gps.pdop}")
    print(f"    Latitude: {gps.latitude_string()}, Longitude: {gps.longitude_string()}, Altitude: {gps.altitude}")
    print(f"    Speed: {gps.speed_string()}, Course: {gps.course}, GEOID Height: {gps.geoid_height}")
    print(f"Date: {gps.date}, Time: {gps.timestamp}")
    print(f"UTC Timestamp: {gps.timestamp}, UTC Offset: {gps.local_offset}")
    

def main():    
    
    # while True:
    #     skew = 0
    #     quiet = True
    #     # dur = mark(skew)
    #     # send_bit('2', dur, quiet)
    #     # send_bit('2', dur, quiet)
    #     # send_bit('2', dur, quiet)
    #     dur = zero(skew)
    #     send_bit('0', dur, quiet)
    #     send_bit('0', dur, quiet)
    #     send_bit('0', dur, quiet)
    #     # dur = one(skew)
    #     # send_bit('1', dur, quiet)
    #     # send_bit('1', dur, quiet)
    #     # send_bit('1', dur, quiet)
    
    load_mapping('/mapping.csv')

    total_zero = 0
    total_one = 0
    
    total_t = 0
    skew = 0.0

    while True:

        dump_gps_data()

        d, m, y = gps.date
        y += 2000
        h, minute, s = gps.timestamp
            
        print(f"Time: {y}-{m}-{d}  {h}:{minute}:{s}")
        code = list(create_timecode(year=y, month=m, day=d, hour=h, minute=minute))

        print(f"Sending Timecode: {''.join(code)}") 

        quiet = False  # Set to True to suppress servo movements

        # reset stats
        total_zero = 0
        total_one = 0
        
        total_t = 0
        skew = 0.0
            
        for index, b in enumerate(code):
            print(f"Sending bit {index}: {b}")
            if b == '2':
                dur = mark(skew)
                send_bit('2', dur, quiet)
            elif b == '0':
                dur = zero(skew)
                send_bit('0', dur, quiet)
                total_zero += dur
                total_t += dur
            elif b == '1':
                dur = one(skew)
                send_bit('1', dur, quiet)
                total_one += dur
                total_t += dur

            skew = total_t - (1 + index)

            d, m, y = gps.date
            y += 2000
            h, minute, s = gps.timestamp
            print(f"Time: {y}-{m}-{d}  {h}:{minute}:{s}  skew == {skew}")

            try:
                # if there is any data in the GPS serial buffer, read it a line, decode it as UTF-8, and print it
                if gps_serial.any():
                    data = gps_serial.readline()  # Read a line from the GPS serial buffer
                    # if there is data and it is a valid NMEA 0183 sentence starting with $ or !
                    if data and (data.startswith(b'$') or data.startswith(b'!')):
                        decoded_data = data.decode('utf-8')
                        for char in decoded_data:
                            # print("Char: ", char)
                            gps.update(char)
                        
                    else:
                        print("No data received from GPS.")
            except Exception as e:
                print(f"Error reading GPS data: {e}")
                
        time.sleep(0.01)
        
if __name__ == "__main__":
    main()
 