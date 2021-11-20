'''
An Azure Function that listens on an IoT Hub event hub compatible endpoint.
When events are received, they are formatted correctly as geospatial data
and saved in CosmosDB
'''
import json
import logging

import azure.functions as func

def main(event: func.EventHubEvent) -> func.Document:
    '''
    An Azure Function that listens on an IoT Hub event hub compatible endpoint.
    When events are received, they are formatted correctly as geospatial data
    and saved in CosmosDB
    '''
    # Extract the body from the IoT Hub event
    body = event.get_body().decode('utf-8')

    logging.info('Python EventHub trigger processed an event: %s', body)

    # Convert teh body string to a JSON object
    json_body = json.loads(body)

    # Build a JSON document to be stored in CosmosDB
    # This record uses the device ID of the sending device as the animal ID
    # and stores the lat/lon in a way that can be saved and queried as GeoSpatial data
    record = {
        'animalid': event.iothub_metadata['connection-device-id'],
        'num_satellites': json_body['gps']['num_satellites'],
        'location':{
            'type':'Point',
            'coordinates':[ json_body['gps']['lon'], json_body['gps']['lat'] ]
        }
    }

    logging.info('Storing record: %s', record)

    return func.Document.from_json(json.dumps(record))
