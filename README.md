# saj_modbus
Python SAJ R5 Inverter Modbus scripts.

**Usage:**

Read inverter details, like serial number, model, software version etc.: 
`python3 read_invertor_details.py --host 0.0.0.0 --port 0`

Read the current date and time from the inverter: 
`python3 read_invertor_datetime.py --host 0.0.0.0 --port 0`

Read error state from the inverter: 
`python3 read_invertor_errors.py --host 0.0.0.0 --port 0`

Read available realtime data: 
`python3 read_realtime_data.py --host 0.0.0.0 --port 0`
