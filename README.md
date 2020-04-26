# Vital-signs

This project is an independent approach to acquire patient data from Philips patient monitors via network interface. It has no association with the Philips corporation.


### Important methodes of piv_data_source.py

#### class piv_data_source.**init**(IP)
When creating a new insctance of **piv_data_source** the correct IP of the patient monitor is required as parameter.

#### class piv_data_source.**start_client**()
Starts the UDP-client thread and begins to acquire data from the monitor.

#### class piv_data_source.**start_watchdog**()
Starts the additional watchdog, that restarts the connection when exceptions occur. If you dont use the watchdog you will have to monitor the current connection yourself. This is necessary because the monitor sometimes terminates the connection spontaneously or does not process requests correctly.

#### class piv_data_source.**halt_client**()
Terminates the connection, the UDP-client and the start_watchdog. Should be called before the object is deleted to terminate the connection correctly.

#### class piv_data_source.**get_vital_signs**()
Returns a list with patient vital signs.

#### class piv_data_source.**get_patient_data**()
Returns a list with patient information admission.

#### class piv_data_source.**refresh_patient_data**()
Reads patient info admission information again to check for changes (usually it is only read once when a new connection is started).

#### class piv_data_source.**check_client_is_working_correctly**()
Returns a boolean whether the connection is working properly.


### Using the Module PIV_data_source.py

```python
from  piv_data_source import piv_data_source

# time module is just used to create some delay to give the monitor time to respond
import time 

# Insert the correct IP of the patient monitor
device = piv_data_source("127.0.0.1")

# Start client and wachdog
device.start_client()
device.start_watchdog()

# delay 10 seconds to give the monitor time to respond
time.sleep(10)

# read patient information and vital signs
print(device.get_patient_data())
print(device.get_vital_signs())

# Terminate connection
device.halt_client()
```


### Example code for plotting data


