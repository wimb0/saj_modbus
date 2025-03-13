# saj_modbus
Python SAJ R5 Inverter Modbus scripts.

**Usage:**

Read available realtime data: 
`python3 read_realtime_data.py --host 0.0.0.0 --port 0`

Read inverter details, like serial number, model, software version etc.: 
`python3 read_inverter_details.py --host 0.0.0.0 --port 0`

Read current error state from the inverter: 
`python3 read_inverter_current_error.py --host 0.0.0.0 --port 0`

Read last 10 errors from the inverter: 
`python3 read_inverter_error_history.py --host 0.0.0.0 --port 0`
