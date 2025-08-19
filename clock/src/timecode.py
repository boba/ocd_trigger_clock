import machine
import time
import utime

# Constants for bit representation
ZERO = '0'
ONE = '1'
MARK = '2'
RESERVED = '0'

# Initialize the RTC
rtc = machine.RTC()

def encode_bcd_to_bitstring(decimal_number):
    """
    Encodes a decimal number into a BCD bit string (MSB first).
    Each byte will contain two BCD digits (packed BCD).
    """
    bit_string = ""
    str_decimal = str(decimal_number)

    # Pad with a leading zero if the number of digits is odd
    if len(str_decimal) % 2 != 0:
        str_decimal = '0' + str_decimal

    for i in range(0, len(str_decimal), 2):
        high_nibble = int(str_decimal[i])
        low_nibble = int(str_decimal[i+1])

        # Convert each nibble to its 4-bit binary representation and append to the bit string
        # bit_string += format(high_nibble, '04b')
        # bit_string += format(low_nibble, '04b')
        bit_string += f'{high_nibble:04b}'
        bit_string += f'{low_nibble:04b}'
    return bit_string


# def encode_bcd_msb_first(decimal_number):
#     """
#     Encodes a decimal number into a BCD byte string, MSB first within each byte.
#     """
#     s_num = str(decimal_number)
#     if len(s_num) % 2 != 0:
#         s_num = '0' + s_num
# 
#     bcd_bytes = bytearray()
#     for i in range(0, len(s_num), 2):
#         msb_digit = int(s_num[i])
#         lsb_digit = int(s_num[i+1])
#         bcd_byte = (msb_digit << 4) | lsb_digit
#         bcd_bytes.append(bcd_byte)
#     return bytes(bcd_bytes)

def decode_bcd_from_bitstring(bcd_digits):
    
    # Reverse the list to match BCD order (most significant digit first)
#     x = _get_minute(55)
#     print(f"DEBUG: 55 == {''.join(x)}")
#     print(f"DEBUG: di == {bcd_digits}")
    
    # bcd_digits.reverse()
    
    # Group bits into nibbles (4 bits each)
    nibbles = [''.join(bcd_digits[i:i + 4]) for i in range(0, len(bcd_digits), 4)]
    # Convert each nibble from binary to decimal and combine
    # return sum(int(nibble, 2) * (10 ** i) for i, nibble in enumerate(reversed(nibbles)))
    return sum(int(nibble, 2) * (10 ** i) for i, nibble in enumerate(reversed(nibbles)))

def _get_bcd(number, l):
    """Convert a number to its BCD representation as a string of bits."""
    
    # print(f"Getting BCD for number: {number}")
    bcd_digits = []
    if number == 0:
        return [ZERO] * l
    while number > 0:
        # Get the least significant digit
        digit = number % 10
        # print(f"digit: {digit}")
        # Convert the digit to its BCD nibble (4-bit representation)
        bcd_nibble = digit & 0xF  # Ensure only the lower 4 bits are taken
        # print(f"bcd_nibble: {bcd_nibble:04b}")
        # Convert the nibble to a binary string of 4 bits
        bcd_digits.append(f"{bcd_nibble:04b}")
        # Remove the least significant digit
        number //= 10

    # Reverse the list to match BCD order (most significant digit first)
    bcd_digits.reverse()

    # create an array of characters to represent the BCD digits
    bcd_digits = [bit for nibble in bcd_digits for bit in nibble]

    # print(f"BCD digits before padding: {bcd_digits}")

    # Pad with leading zeros to ensure we have 8 bits
    while len(bcd_digits) < l:
        bcd_digits.insert(0, ZERO)

    return bcd_digits

# def _get_minute(minute):
#     return _get_bcd(minute, l=8)

# def _get_hour(hour):
#     return _get_bcd(hour, l=8)


def _get_days(year, month, day):
    # d = datetime.datetime(year, month, day)
    # Set the datetime (e.g., to January 1, 2025, 10:30:00)
    # (year, month, day, hour, minute, second, weekday, yearday)
    d = rtc.datetime((year, month, day, 0, 0, 0, 0, 0))
    # doy = d.timetuple().tm_yday
    day = time.localtime()[7]

    return _get_bcd(day, l=12)


def _get_year(year):
    return _get_bcd(year, l=8)


def _set_minute_bits(code, minute):
    """
    Set minute bits in the timecode array.

    Args:
        code (list): The timecode array to modify.
        minute (int): The minute value to encode.

    Returns:
        None: The function modifies the code in place.

    This function sets the minute bits in the timecode array based on the provided minute value.
    It encodes the minute in BCD format and updates the relevant bits in the code array

    Bit 1: Minutes, 40
    Bit 2: Minutes, 20
    Bit 3: Minutes, 10
    Bit 4: RESERVED
    Bit 5: Minutes, 8
    Bit 6: Minutes, 4
    Bit 7: Minutes, 2
    Bit 8: Minutes, 1

    """
#     minute_bits = _get_minute(minute)
# 
#     print(f"DEBUG: minute           = {minute}")
#     print(f"DEBUG: minute_bits      = {minute_bits}")
# 
#     bcd = encode_bcd_msb_first(minute)
#     print(f"DEBUG: bcd              = {bcd}")
#     print(f"DEBUG: bcd str          = {bin(bytearray(bcd)[0])}")
# 
    bstr = encode_bcd_to_bitstring(minute)
#     print(f"DEBUG: bcd              = {bcd}")
#     print(f"DEBUG: bit str          = {bstr}")
    
    # minutes_bits = list(minute_bits)
    # minutes_bits = list(bin(bytearray(bcd)[0]))
    minute_bits = list(bstr)
    code[1:4] = minute_bits[1:4]
    code[4:5] = [RESERVED]  # 4th bit is always RESERVED
    code[5:9] = minute_bits[4:8]

    #print(f"DEBUG: _set_minute_bits = {code[1:9]}")
    return code

def _decode_minute(bits):
    # print(f"DEBUG: _decode_minute {bits}")
    # bits = list(bits)
    # bits[4] = ZERO
    # print(f"DEBUG: _decode_minute {''.join(bits)}")
    # value = decode_bcd_from_bitstring(''.join(bits))
    #return value

    # print(f"DEBUG: _decode_minutes {bits}")
    bits = list(bits)
    bits = [ZERO] + bits[0:4] + bits[5:8]
    # print(f"DEBUG: _decode_minute {''.join(bits)}")
    value = decode_bcd_from_bitstring(''.join(bits))
    return value

def _decode_hour(bits):
    #print(f"DEBUG: _decode_hour {''.join(bits)}")
    bits = list(bits)
    bits = [ZERO] + bits[0:3] + bits[4:8]
    #print(f"DEBUG: _decode_hour {''.join(bits)}")

    value = decode_bcd_from_bitstring(''.join(bits))
    return value

def _decode_day_of_year(bits):
    
    # print(f"DEBUG: _decode_day_of_year {''.join(bits)}")
    bits = list(bits)
    bits = [ZERO] + [ZERO] + bits[2:4] + bits[5:9] + bits[10:14]
    # print(f"DEBUG: _decode_day_of_year {''.join(bits)}")

    value = decode_bcd_from_bitstring(''.join(bits))
    return value

def _decode_year(bits):
    
    #print(f"DEBUG: _decode_year {''.join(bits)}")
    bits = list(bits)
    bits = bits[0:4] + bits[5:9]
    #print(f"DEBUG: _decode_year {''.join(bits)}")

    value = decode_bcd_from_bitstring(''.join(bits))
    return value

def _decode_date(year, day_of_year):
    year = 2000 + year # ...a bold assumption

    # Create a tuple representing January 1st of the given year
    jan1_tuple = (year, 1, 1, 0, 0, 0, 0, 0)
    
    # Get the timestamp for January 1st
    jan1_timestamp = utime.mktime(jan1_tuple)
    
    # Add the number of days (day_of_year - 1 because day_of_year is 1-indexed)
    target_timestamp = jan1_timestamp + (day_of_year - 1) * 24 * 60 * 60
    
    # Convert the timestamp back to a datetime tuple
    date_tuple = utime.localtime(target_timestamp)
    
    # Extract year, month, and day from the resulting tuple
    return date_tuple[0], date_tuple[1], date_tuple[2]

def _set_hour_bits(code, hour):
    """
    Set hour bits in the timecode array.

    Args:
        code (list): The timecode array to modify.
        hour (int): The hour value to encode.

    Returns:
        None: The function modifies the code in place.

    This function sets the hour bits in the timecode array based on the provided hour value.
    It encodes the hour in BCD format and updates the relevant bits in the code array.

    Bit 12: Hours, 20
    Bit 13: Hours, 10
    Bit 14: RESERVED
    Bit 15: Hours, 8
    Bit 16: Hours, 4
    Bit 17: Hours, 2
    Bit 18: Hours, 1
    """
    
    # hour_bits = _get_hour(hour)
    # print(f"DEBUG: hour            = {hour}")
    # print(f"DEBUG: hour_bits       = {hour_bits}")
    
    bstr = encode_bcd_to_bitstring(hour)
    hour_bits = list(bstr)
    
    code[12:14] = hour_bits[2:4]
    code[14:15] = [RESERVED]
    code[15:19] = hour_bits[4:8]

    # print(f"DEBUG: _set_hour_bits  = {code[12:20]}")
    return code

def _set_days_bits(code, year, month, day):
    """
    Set day-of-year bits in the timecode array.

    Args:
        code (list): The timecode array to modify.
        year (int): The year value.
        month (int): The month value.
        day (int): The day value.

    Returns:
        None: The function modifies the code in place.

    This function sets the day-of-year bits in the timecode array based on the provided date.
    It encodes the day-of-year in BCD format and updates the relevant bits in the code array.

    Bit 20: RESERVED
    Bit 21: RESERVED
    Bit 22: Day-of-year, 200
    Bit 23: Day-of-year, 100
    Bit 24: RESERVED
    Bit 25: Day-of-year, 80
    Bit 26: Day-of-year, 40
    Bit 27: Day-of-year, 20
    Bit 28: Day-of-year, 10
    Bit 29: MARK
    Bit 30: Day of year 8
    Bit 31: Day of year 4
    Bit 32: Day of year 2
    Bit 33: Day of year 1
    """
    days_bits = _get_days(year, month, day)
    print(f"DEBUG: Day {year}-{month}-{day} == {''.join(days_bits)} == {''.join(days_bits)}")

#     # d = datetime.datetime(year, month, day)
#     # Set the datetime (e.g., to January 1, 2025, 10:30:00)
#     # (year, month, day, hour, minute, second, weekday, yearday)
    # d = rtc.datetime((year, month, day, 0, 0, 0, 0, 0))
#     day = d.timetuple().tm_yday
    # print(f"DEBUG: Day 1 == {d}")

    print(f"DEBUG: _set_days_bits({year}-{month}-{day})")
    datetime_tuple = rtc.datetime((year, month, day, 0, 0, 0, 0, 0))
    struct_time = utime.localtime(utime.time())
    day_of_year = struct_time[7]
    print("Current datetime:", datetime_tuple)
    print("Day of the year:", day_of_year)

    # day = time.localtime()[7]
    # print(f"DEBUG: Day 2 == {day}")

    # bstr = encode_bcd_to_bitstring(day)
    bstr = encode_bcd_to_bitstring(day_of_year)
    # print(f"DEBUG: Day {year}-{month}-{day} == {''.join(days_bits)} == {bstr}")
#     if len(bstr) > 12:
#         days_bits = list(bstr)[-12:] # drop the first four bits
#     else :
#         bstr = f"{bstr:0>12}"
#         days_bits = list(bstr) # make sure we have 12 bits

    bstr = f"{bstr:0>12}"
    days_bits = list(bstr)[-12:] # drop the first four bits

    print(f"DEBUG: Day {year}-{month}-{day} == {''.join(days_bits)} == {''.join(days_bits)}")

    code[20:24] = days_bits[0:4]
    code[24:25] = [RESERVED]  # 24th bit is always RESERVED
    code[25:29] = days_bits[4:8]
    code[29:30] = [MARK]
    code[30:34] = days_bits[8:12]


def create_timecode(year=2025, month=1, day=1, hour=0, minute=0, dst=False):
    """
    Generates a timecode string from the provided date and time components.

    args:
        year (int): The year (default is 2025).
        month (int): The month (1-12, default is 1).
        day (int): The day of the month (1-31, default is 1).
        hour (int): The hour of the day (0-23, default is 0).
        minute (int): The minute of the hour (0-59, default is 0).

    Returns:
        str: A string representing the WWVB timecode.

    Example: 200000010200000001120010000012100000101200010001020101000112

    $> wwvbgen -m 1 2025 08 06 03 02 && python timecode.py
    WWVB timecode: year=2025 days=218 hour=03 min=02 dst=3 ut1=100 ly=0 ls=0
    2025-218 03:02  200000010200000001120010000012100000101200010001020101000112

    """

    # 60 bit timecode array
    code = ['X'] * 60

    # Data frame marker
    code[0:1] = [MARK]

    # Bits 1-8: Minutes
    code = _set_minute_bits(code, minute)

    code[9:10] = [MARK]  # 9th bit is always mark

    # Bits 10-11: RESERVED
    code[10:11] = [RESERVED]  # 10th bit is always RESERVED
    code[11:12] = [RESERVED]  # 11th bit is always RESERVED

    # Bits 12-18: Hours
    code = _set_hour_bits(code, hour)

    code[19:20] = [MARK]  # 19th bit is always mark

    # Bits 20-21: Reserved (always 0)
    code[20:21] = [RESERVED]  # 20th bit is always RESERVED
    code[21:22] = [RESERVED]  # 21st bit is always RESERVED

    # Bits 22-28: Day of year
    # TODO: should this be setting bits 20 and 21 or are they reserved as above?
    _set_days_bits(code, year, month, day)

    code[34:35] = [RESERVED]  # 34th bit is always RESERVED
    code[35:36] = [RESERVED]  # 35th bit is always RESERVED0

    # 36-38 DUT1 sign
    code[36:37] = [ONE] # TODO: get this working later
    code[37:38] = [RESERVED] # TODO: get this working later
    code[38:39] = [ONE] # TODO: get this working later
         
    code[39:40] = [MARK]  # 39th bit is always mark

    # DUT1 time correction 40, 41, 42, 43)
    code[40:41] = [RESERVED] # TODO: get this working later
    code[41:42] = [RESERVED] # TODO: get this working later
    code[42:43] = [RESERVED] # TODO: get this working later
    code[43:44] = [RESERVED] # TODO: get this working later

    code[44:45] = [RESERVED]  # 44th bit is always RESERVED
    code[45:50] = _get_year(25)[0:4]
    code[49:50] = [MARK]  # 49th bit is always mark
    code[50:55] = _get_year(25)[4:8]
    code[54:55] = [RESERVED]  # 54th bit is always RESERVED

    # 55 leap year indicator
    code[55:56] = [RESERVED] # TODO: get this working later

    # 56 leap second indicator
    code[56:57] = [RESERVED] # TODO: get this working later

    # 57-58 DST status
    if dst:
        code[57:58] = [ONE] # TODO: get this working later
        code[58:59] = [ONE] # TODO: get this working later
    else:
        code[57:58] = [ZERO] # TODO: get this working later
        code[58:59] = [ZERO] # TODO: get this working later

    # mark
    code[59:60] = [MARK]  # 59th bit is always mark

    # create the time code string
    timecode = ''.join(map(str, code))

    return timecode

def _test(year=2025, month=0, day=0, hour=0, minute=0, dst=False, compare=None):
    
    # WWVB timecode: year=2025 days=230 hour=16 min=05 dst=3 ut1=100 ly=0 ls=0
    # 2025-230 16:05  200000101200010011020010000112000000101200010001020101000112
    #                 012345678901234567890123456789012345678901234567890123456789
    #                          1         2         3         4         5         

    # wwvbgen -m 1 2025 08 18 13 50
    # WWVB timecode: year=2025 days=230 hour=13 min=50 dst=3 ut1=100 ly=0 ls=0
    #
    #                          1         2         3         4         5         
    #                 012345678901234567890123456789012345678901234567890123456789
    # 2025-230 13:50  210100000200010001120010000112000000101200010001020101000112

    code = create_timecode(year=year, month=month, day=day, hour=hour, minute=minute, dst=dst)

    print(f'                    1         2         3         4         5          ')
    print(f'          012345678901234567890123456789012345678901234567890123456789')
    print(f"Expected: {compare}")
    print(f"Actual  : {code}")
    
    c = ''.join([' ' if a == b else '^' for a, b in zip(code, compare)])
    print(f"Diff    : {c}")
    
    value = _decode_hour(code[11:19])
    print(f"Hour    : {hour} == {value}")

    value = _decode_minute(code[1:9])
    print(f"Minutes : {minute} == {value}")

    value = _decode_day_of_year(code[20:34])
    print(f"DoY     : ??? == {value}")

    value = _decode_year(code[45:54])
    print(f"Year    : {year} == {value}")

    y, m, d = _decode_date(_decode_year(code[45:54]), _decode_day_of_year(code[20:34]))
    print(f"Date    : {year}-{month}-{day} == {y}-{m}-{d}")

def test():
    # wwvbgen --dut1 0 -m 1 2025 01 01 00 00
    # WWVB timecode: year=2025 days=001 hour=00 min=00 dst=0 ut1=0 ly=0 ls=0
    # 2025-001 00:00  200000000200000000020000000002000100101200000001020101000002
    _test(year=2025, month=1, day=1, hour=0, minute=0, dst=False, compare='200000000200000000020000000002000100101200000001020101000002')

    # wwvbgen --dut1 0 -m 1 2025 01 01 01 01
    # WWVB timecode: year=2025 days=001 hour=01 min=01 dst=0 ut1=0 ly=0 ls=0
    # 2025-001 01:01  200000001200000000120000000002000100101200000001020101000002
    _test(year=2025, month=1, day=1, hour=1, minute=1, dst=False, compare='200000001200000000120000000002000100101200000001020101000002')

    # wwvbgen --dut1 0 -m 1 2025 08 18 14 25
    # WWVB timecode: year=2025 days=230 hour=14 min=25 dst=3 ut1=0 ly=0 ls=0
    # 2025-230 14:25  201000101200010010020010000112000000101200000001020101000112
    _test(year=2025, month=8, day=18, hour=14, minute=25, dst=True, compare='201000101200010010020010000112000000101200000001020101000112')

    # wwvbgen --dut1 0 -m 1 2025 12 27 23 55
    # WWVB timecode: year=2025 days=361 hour=23 min=55 dst=0 ut1=0 ly=0 ls=0
    # 2025-361 23:55  210100101200100001120011001102000100101200000001020101000002
    _test(year=2025, month=12, day=27, hour=23, minute=55, dst=False, compare='210100101200100001120011001102000100101200000001020101000002')

    print(f"Decoding Tests...")
    # enc = encode_bcd_msb_first(55)
    # dec = decode_bcd_msb_first(enc)
    # print(type(enc))
    # print(bin(bytearray(enc)[0]))
    # print(f"55 = {enc.decode("utf-8")} == {dec}")
    
    
    # enc = encode_bcd_to_bitstring(55)
    # print(type(enc))
    # print(enc)
    # print(f"55 = {enc} == {dec}")
    
          
def main():
    
    # WWVB timecode: year=2025 days=230 hour=16 min=05 dst=3 ut1=100 ly=0 ls=0
    # 2025-230 16:05  200000101200010011020010000112000000101200010001020101000112
    #                 012345678901234567890123456789012345678901234567890123456789
    #                          1         2         3         4         5         

    t = '200000101200010011020010000112000000101200010001020101000112'
    c = create_timecode(year=2025, month=8, day=18, hour=16, minute=5)

    print(t)
    print(c)
    print('012345678901234567890123456789012345678901234567890123456789')
    print('         1         2         3         4         5          ')
    
if __name__ == "__main__":
    main()
