# Timecodes


## Overview
This project uses the time code format utilized by [WWVB](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwvb). It is based on the IRIG timecode, but the bit encoding and order differs from [IRIG](https://en.wikipedia.org/wiki/IRIG_timecode) standards.  This code contains the year, day of the year, hour minute, and other relevant information about the current time. It also precisely marks the beginning of each minute. Since the United States has multiple timezones, the time is sent in [Coordinated Universal Time (UTC)](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) and receivers can interpret the provided daylight savings time indicators and offsets as needed to derive the local time.

[WWVB](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwvb) transmits on a 60 kHz carrier at about 70 kW ERP.  The timecode is derived from a set of atomic clocks at the receiver site. The timecode is modulated over the carrier using pulse-width modulation and amplitude-shift keying at one bit per second. This means that it will take one minute to send the entire 60 bit frame for a complete timecode. 

The amplitude modulation of the signal uses different levels of power to represent zero, one, and mark values for each bit of the timecode. The phase modulated signal uses [binary phase-shift keying (BPSK)](https://en.wikipedia.org/wiki/Phase-shift_keying#Binary_phase-shift_keying_(BPSK)) which inverts the phase of the carrier 180 degrees for one second to represent a one while a zero maintains the original phase of the carrier signal. There is more nuance to the BPSK signal than we should into for this project.

To meet the goals of this project, we can simplify the PWM/AM modulation by simply sending setting a 

## WWVB Timecode Structure

| Bit | Meaning                | Example                                                                          |
| --- | ---------------------- | -------------------------------------------------------------------------------- |
| :00 | Frame reference Marker |                                                                                  |
| :01 | Minutes   (00-59)      |                                                                                  |
| :02 | Minutes                |                                                                                  |
| :03 | Minutes                |                                                                                  |
| :04 | Minutes                |                                                                                  |
| :05 | Minutes                |                                                                                  |
| :06 | Minutes                |                                                                                  |
| :07 | Minutes                |                                                                                  |
| :08 | Minutes                |                                                                                  |
| :09 | Marker                 |                                                                                  |
| :10 | Unused (0)             |                                                                                  |
| :11 | Unused (0)             |                                                                                  |
| :12 | Hours (00-23)          |                                                                                  |
| :13 | Hours                  |                                                                                  |
| :14 | Hours                  |                                                                                  |
| :15 | Hours                  |                                                                                  |
| :16 | Hours                  |                                                                                  |
| :17 | Hours                  |                                                                                  |
| :18 | Hours                  |                                                                                  |
| :19 | Marker                 |                                                                                  |
| :20 | Unused (0)             |                                                                                  |
| :21 | Unused (0)             |                                                                                  |
| :22 | Day of Year            | 1 == Jan 1, 365 == Dec 31 (366 for leap years)                                   |
| :23 | Day of Year            |                                                                                  |
| :24 | Day of Year            |                                                                                  |
| :25 | Day of Year            |                                                                                  |
| :26 | Day of Year            |                                                                                  |
| :27 | Day of Year            |                                                                                  |
| :28 | Day of Year            |                                                                                  |
| :29 | Marker                 |                                                                                  |
| :30 | Day of Year            |                                                                                  |
| :31 | Day of Year            |                                                                                  |
| :32 | Day of Year            |                                                                                  |
| :33 | Day of Year            |                                                                                  |
| :34 | Unused (0)             |                                                                                  |
| :35 | Unused (0)             |                                                                                  |
| :36 | DUT1 sign              | Bits 36-38 == 101 for + DUT, 010 for - DUT                                       |
| :37 | DUT1 sign              |                                                                                  |
| :38 | DUT1 sign              |                                                                                  |
| :39 | Marker                 |                                                                                  |
| :40 | DUT1 value             | 0-0.9 s                                                                          |
| :41 | DUT1 value             |                                                                                  |
| :42 | DUT1 value             |                                                                                  |
| :43 | DUT1 value             |                                                                                  |
| :44 | Unused (0)             |                                                                                  |
| :45 | Year (00-99)           |                                                                                  |
| :46 | Year                   |                                                                                  |
| :47 | Year                   |                                                                                  |
| :48 | Year                   |                                                                                  |
| :49 | Marker                 |                                                                                  |
| :50 | Year                   |                                                                                  |
| :51 | Year                   |                                                                                  |
| :52 | Year                   |                                                                                  |
| :53 | Year                   |                                                                                  |
| :54 | Unused (0)             |                                                                                  |
| :55 | Leap year indicator    |                                                                                  |
| :56 | Leap second at EOM     |                                                                                  |
| :57 | DST status value       | 00 == No DST, 10 == DST starts today, 11 11 == DST in efft, 01 == DST ends today |
| :58 | DST status value       |                                                                                  |
| :59 | Marker                 |                                                                                  |


References:
- [WWVB Time Signal Station](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwvb) 
- [IRIG Timecode](https://en.wikipedia.org/wiki/IRIG_timecode)
