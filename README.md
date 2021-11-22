# GPS animal tracker

This repo contains resources for my Microsoft Student Summit Africa session on using GPS to track animals.

Most of this repo is demo code, showing how to capture and decode data from a GPS sensor using Python and a Raspberry Pi. This code was tested using a [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), and a [Seeed Grove GPS Air530 sensor](https://www.seeedstudio.com/Grove-GPS-Air530-p-4584.html) connected via a [Grove Base hat](https://www.seeedstudio.com/Grove-Base-Hat-for-Raspberry-Pi.html).

You can find instructions on setting up this hardware, and configuring Raspberry Pi OS in the [Pi GPS sensor section of the location tracking project in the IoT for Beginners curriculum](https://github.com/microsoft/IoT-For-Beginners/blob/main/3-transport/lessons/1-location-tracking/pi-gps-sensor.md).

GPS data is received from the sensor over UART as NMEA sentences. You can learn more about this data in the [location tracking project in the IoT for Beginners curriculum](https://github.com/microsoft/IoT-For-Beginners/blob/main/3-transport)

## Structure of this repo

This repo has the following code samples in it:

* [`device/print-gps-data`](./device/print-gps-data) - Code to read NMEA sentences from the GPS sensor print them to the console
* [`device/decode-gps-data`](./device/decode-gps-data) - Code to read NMEA sentences from the GPS sensor and decode them to get latitude and longitude
* [`device/send-gps-data`](./device/send-gps-data) - Code to read NMEA sentences from the GPS sensor, decode them to get latitude and longitude, then send this to Azure IoT Hub
* [`functions`](./functions) - An example Azure Functions app that will listen to the events sent to Azure IoT Hub, and use these to build geospatial records that are then saved in CosmosDB

## Using this code

Clone this repo onto your Raspberry Pi, and on your PC or Mac if you want to run the functions.

The first 2 demos (`print-gps-data` anf `decode-gps-data`) just require a Raspberry Pi set up with the Grove GPS sensor. The code folders contain a `requirements.txt` file that will need to be installed with Pip to install the relevant packages. When run, the code will output with NMEA sentences, or GPS coordinates, depending on which demo you ran.

To run the `send-gps-data` demo, you will need an instance of Azure IoT Hub. You can find instructions on creating this service in the [Create an IoT Hub documentation](https://docs.microsoft.com/azure/iot-hub/iot-hub-create-through-portal?WT.mc_id=academic-49550-jabenn). Once created, create a device and get the connection string. This then needs to be added to a file called `.env` in the same folder as this demo:

```output
CONNECTION_STRING=<Your IoT Hub device connection string goes here>
```

When run this will capture GPS coordinates and send these to your IoT Hub.

Once `send-gps-data` is running, you can run the `functions` demo using the [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local?tabs=v4%2Clinux%2Ccsharp%2Cportal%2Cbash%2Ckeda?WT.mc_id=academic-49550-jabenn). This demo needs an instance of Cosmos DB, and you can find instructions on creating this in the [Create an Azure Cosmos account, database, container, and items documentation](https://docs.microsoft.com/azure/cosmos-db/sql/create-cosmosdb-resources-portal?WT.mc_id=academic-49550-jabenn). Once the account is created, create a database called `animals`, and a container called `locations`, with the partition key set to `/animalid`.

You will need to set the following in the `local.settings.json` file:

```json
{
    "IOT_HUB_CONNECTION_STRING": "<The event hub compatible endpoint for your IoT Hub>",
    "COSMOSDB_CONNECTION_STRING": "<The connection string for your CosmosDB account>"
}
```

## Additional resources

* You can learn more about IoT, including how to track and manage location data, from [IoT for Beginners, our 24 lesson curriculum all about IoT](https://aka.ms/iot-beginners)
* If you want to learn more about using Microsoft IoT services, check out these [IoT Learning paths on Microsoft Learn](https://docs.microsoft.com/users/jimbobbennett/collections/ke2ehd351jopwr?WT.mc_id=academic-49550-jabenn)
* You can plot data using Azure Maps, and to learn more about this check out these [Azure Maps learning paths on Microsoft Learn](https://docs.microsoft.com/users/jimbobbennett/collections/30p0c0mgg2n23g?WT.mc_id=academic-49550-jabenn)
* If you want to add an industry certification to your resume, check out the [AZ-220 Microsoft Azure IoT developer certification](https://docs.microsoft.com/learn/certifications/exams/az-220?WT.mc_id=academic-49550-jabenn)
