'''
Sample code showing how to send GPS coordinates to Azure IoT Hub.

You can learn more about tracking with GPS and managing GPS data in the third project of
the IoT for Beginners curriculum:

https://github.com/microsoft/IoT-For-Beginners/tree/main/3-transport
'''
import asyncio
import json
import os
from typing import NamedTuple

# The pynmea2 library is used to decode NMEA sentences
# These are the messages that are sent by GPS devices
# You can read more about NMEA sentences at
# https://github.com/microsoft/IoT-For-Beginners/tree/main/3-transport/lessons/1-location-tracking#nmea-gps-data
import pynmea2

# The pyserial library is used to read serial data over a UART connection to
# the GPS sensor
import serial

# The azure-iot-device package contains classes to connect to Azure IoT Hub
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient

# THe python-dotenv package allows loading environment variables from .env files
from dotenv import load_dotenv

class LatLon(NamedTuple):
    '''
    A named tuple type to define a GPS coordinate as a latitude and longitude,
    along with the number of satellites use to get the fix
    '''
    lat: float
    lon: float
    num_satellites: int

# Load the .env file into environment variables. This file allows the connection string to be
# kept out of code and loaded on demand. The .env file should not be stored in source code control.
# In this sample the file is added to show what you need to add to this file.
load_dotenv()

# Get the IoT Hub connection string from an environment variable
CONNECTION_STRING = os.environ['CONNECTION_STRING']

def flush_serial(serial_conn: serial.Serial) -> None:
    '''
    Drains the serial data from the UART connection.
    This is done so we can read data every minute, and ignore the data in-between
    '''
    # Clear and flush the input buffer to remove all data
    serial_conn.reset_input_buffer()
    serial_conn.flush()

    # Try to read and decode a line. This is needed as the data is utf-8, so can be variable width
    # and we don't want to read a partial line that starts part-way through a variable width character.
    # The code here will read until is gets a full line that can be decoded successfully
    line = None
    while not line:
        try:
            # Decode the line as utf-8
            line = serial_conn.readline().decode('utf-8').strip()
        except UnicodeDecodeError:
            # If we are reading part way through a character, this exception will be thrown.
            # Reset the line and read again
            line = None

async def connect_to_iot_hub() -> IoTHubDeviceClient:
    '''
    Make a connection to Azure IoT Hub using the connection string.
    This returns a device client instance that can be used to send telemetry or
    subscribe to direct methods.
    '''
    # Create a device client from the connection string. This client starts off disconnected
    device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    print('Connecting')
    # Connect the device client to Azure IoT Hub
    await device_client.connect()
    print('Connected')

    return device_client

def get_next_location(serial_conn: serial.Serial) -> LatLon:
    '''
    Gets the next lat and lon pair from the GPS sensor.

    This reads data from the serial port until a GGA sentence is read - this is the sentence
    with the GPS coordinates read from satelites. Once this sentence is read, the lat and lon
    are returned as a tuple.

    If no GPS coordinates are found, -999, -999 is returned.
    '''
    # Drain the serial buffer as we want the latest GPS reading
    flush_serial(serial_conn)

    # Set up a retry count - this code will try 100 times to get a valid
    # GGA sentence, that is a sentence that has GPS coordinates from multiple
    # satellites
    retry = 0

    # Start looping looking for a GGA sentence
    while retry < 100:
        # Read the next line from the serial buffer
        line = serial_conn.readline().decode('utf-8')

        # Try reading a sentence from the line read from the GPS sensor.
        # If the line read is incomplete, the sentence will fail to parse, so we can try again
        sentence = None
        while sentence is None:
            try:
                # Use PyNMEA to parse the NMEA sentence from the line of data
                sentence = pynmea2.parse(line)
            except pynmea2.nmea.ParseError:
                # If we get a parse error, read the next line
                line = serial_conn.readline().decode('utf-8')

        # Each sentence has a type specifying the data it has. This code is after a GGA
        # sentence which has the GPS position
        if sentence.sentence_type == 'GGA':
            # If we have a GGA, read the lat and lon. The values are in degrees and minutes, so
            # convert to decimal degrees
            lat = pynmea2.dm_to_sd(sentence.lat)
            lon = pynmea2.dm_to_sd(sentence.lon)

            # The positions are given as N/S or E/W. For decimal degrees, these should be converted
            # to positive or negative values. S of the equator is negative, so is west of the
            # prime meridian
            if sentence.lat_dir == 'S':
                lat = lat * -1

            if sentence.lon_dir == 'W':
                lon = lon * -1

            # Return the lat, lon, and number of satellites as a tuple
            return LatLon(lat, lon, sentence.num_sats)

        # Increment the retry
        retry += 1

    # If we don't successfully get a lat and lon, return -999,-999
    return LatLon(-999, -999)

async def send_message(device_client: IoTHubDeviceClient, lat_lon: LatLon) -> None:
    '''
    Send a message to the IoT device client with the lat and lon.
    The message is in the following format:

    {
        "gps": {
            "lat": <lat>,
            "lon": <lon>,
            "num_satellites": <num_satellites>
        }
    }

    where <lat> and <lon> are floating point numbers and <num_satellites> is an int
    '''
    # Build the message as JSON
    message_json = { 'gps' : { 'lat':lat_lon.lat, 'lon':lat_lon.lon, 'num_satellites': lat_lon.num_satellites } }

    print('Sending telemetry', message_json)

    # Create the message as a string created from the JSON
    message = Message(json.dumps(message_json))

    # Send the message to Azure IoT Hub as a device to cloud (D2C) message
    await device_client.send_message(message)

async def main() -> None:
    '''
    The main loop of the application.

    This connects to the serial port, connects this device to IoT Hub, then sends GPS coordinates.
    The coordinates are polled for every 60 seconds in an infinite loop and sent to Azure IoT Hub
    '''
    # Connect to the GPS sensor. This is always a serial connection at 9,600 baud
    # on the /dev/ttyAMA0 port
    serial_connection = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

    # Clear out any serial data to ensure we are reading full sentences
    flush_serial(serial_connection)

    # Connect this device to Azure IoT Hub
    device_client = await connect_to_iot_hub()

    # The main loop of the application. Loop forever
    while True:
        # Get the latest GPS coordinates
        lat_lon = get_next_location(serial_connection)

        # If there isn't a valid set of coordinates available, the call to get_next_location will
        # return -999, -999 as the location. Test for this and only proceed if the coordinates are valid
        if lat_lon.lat > -999 and lat_lon.lon > -999:
            # If the coordinates are valid, send the lat and lon as a message to Azure IoT Hub
            await send_message(device_client, lat_lon)

        # Sleep for 60 seconds between coordinated
        await asyncio.sleep(60)

# Start the main loop running.
asyncio.run(main())
