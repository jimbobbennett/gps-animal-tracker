'''
Sample code showing how to read NMEA sentences from a GPS sensor and show the data.

You can learn more about tracking with GPS and managing GPS data in the third project of
the IoT for Beginners curriculum:

https://github.com/microsoft/IoT-For-Beginners/tree/main/3-transport
'''

# The pyserial library is used to read serial data over a UART connection to
# the GPS sensor
import serial

def flush_serial(serial_conn: serial.Serial) -> None:
    '''
    Drains the serial data from the UART connection.
    This is done so we can read data every 10 seconds, and ignore the data in-between
    '''
    # Clear and flush the input buffer to remove all data
    serial_conn.reset_input_buffer()
    serial_conn.flush()

    # Try to read and decode a line. This is needed as the data is utf-8, so can be variable width
    # and we don't want to read a partial line that starts part-way through a variable width character.
    # The code here will read until is gets a full line that can be decoded successfully
    read_line = None
    while read_line is None:
        try:
            # Decode the line as utf-8
            read_line = serial_conn.readline().decode('utf-8')
        except UnicodeDecodeError:
            # If we are reading part way through a character, this exception will be thrown.
            # Reset the line and read again
            read_line = None

# Connect to the GPS sensor. This is always a serial connection at 9,600 baud
# on the /dev/ttyAMA0 port
serial_connection = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

# Clear out any serial data to ensure we are reading full sentences
flush_serial(serial_connection)

# The main loop of the application. Loop forever
# There is no pause here - the application will block whilst waiting for a new line from the serial port
while True:
    # Read the line of data from the serial connection
    line = serial_connection.readline().decode('utf-8').strip()
    if line:
        print(line)
