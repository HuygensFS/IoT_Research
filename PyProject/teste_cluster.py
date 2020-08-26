# if you want logging
import logging
logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

import zigate
z = zigate.connect(port=None) # Leave None to auto-discover the port

print(z.get_version())
OrderedDict([('major', 1), ('installer', '30c'), ('rssi', 0), ('version', '3.0c')])

print(z.get_version_text())


# refresh devices list
z.get_devices_list()

# start inclusion mode
z.permit_join()
z.is_permitting_join()
True

# list devices
z.devices
[Device '677c' , Device 'b8ce' , Device '92a7' , Device '59ef' ]
z.devices[0].addr
'677c'

# get all discovered endpoints
>>> z.devices[0].endpoints
{1: {
  'clusters': {0: Cluster 0 General: Basic,
   1026: Cluster 1026 Measurement: Temperature,
   1027: Cluster 1027 Measurement: Atmospheric Pressure,
   1029: Cluster 1029 Measurement: Humidity},
  }}


# get well known attributes
>>> for attribute in z.devices[0].properties:
     print(attribute)
{'data': 'lumi.weather', 'name': 'type', 'attribute': 5, 'value': 'lumi.weather'}
{'data': '0121c70b0421a8010521090006240100000000642932096521851c662bd87c01000a210000', 'name': 'battery', 'value': 3.015, 'unit': 'V', 'attribute': 65281}
{'data': -1983, 'name': 'temperature', 'value': -19.83, 'unit': '°C', 'attribute': 0}
{'data': 9779, 'name': 'pressure2', 'value': 977.9, 'unit': 'mb', 'attribute': 16}
{'data': 977, 'name': 'pressure', 'value': 977, 'unit': 'mb', 'attribute': 0}
{'data': 4484, 'name': 'humidity', 'value': 44.84, 'unit': '%', 'attribute': 0}

# get specific property
>>> z.devices[0].get_property('temperature')
{'data': -1983,
 'name': 'temperature',
 'value': -19.83,
 'unit': '°C',
 'attribute': 0}

 # call action on devices
 z.action_onoff('b8ce', 1, zigate.ON)

 # or from devices
 z.devices[1].action_onoff(zigate.ON)

 # OTA process
 # Load image and send headers to ZiGate
 z.ota_load_image('path/to/ota/image_file.ota')
 # Tell client that image is available
 z.ota_image_notify('addr')
 # It will take client usually couple seconds to query headers
 # from server. Upgrade process start automatically if correct
 # headers are loaded to ZiGate. If you have logging level debug
 # enabled you will get automatically progress updates.
 # Manually check ota status - logging level INFO
 z.get_ota_status()
 # Whole upgrade process time depends on device and ota image size
 # Upgrading ikea bulb took ~15 minutes
 # Upgrading ikea remote took ~45 minutes
