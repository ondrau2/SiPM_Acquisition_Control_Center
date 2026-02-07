# UDP Packet Reception Implementation

## Overview
This implementation adds UDP packet reception capability to the SiPM Acquisition Control Center GUI, allowing users to receive data packets via UDP in addition to the existing serial interface.

## Features
- **Connection Type Selection**: Users can choose between "Serial" and "UDP" connection types
- **UDP Configuration**: Configurable IP address and port settings for UDP reception
- **Same Packet Format**: UDP packets use the same 7-byte format as serial packets
- **Seamless Integration**: UDP packets are processed through the same message handling pipeline

## Packet Format
Both Serial and UDP use the same 7-byte packet structure:
```
Byte 0: Start Symbol (0x55)
Byte 1: Message Header/ID
Bytes 2-5: Data (4 bytes)
Byte 6: CRC8 checksum
```

## Usage

### Selecting Connection Type
1. Open the GUI
2. In the connection panel (top of the window), select "Connection" dropdown
3. Choose either "Serial" or "UDP"

### Configuring UDP Connection
When UDP is selected:
1. Enter the IP address to bind to (default: 0.0.0.0 for all interfaces)
2. Enter the UDP port number (default: 5005)
3. Click "Connect" to start receiving UDP packets
4. Click "Close" to stop receiving

### Configuring Serial Connection
When Serial is selected:
1. Click "Refresh" to scan for available COM ports
2. Select the desired COM port from the dropdown
3. Click "Connect" to establish serial connection
4. Click "Close" to disconnect

## Implementation Details

### Files Modified
- **GUI_lib/ConnectionPannelContents.py**: Updated connection panel to support both Serial and UDP
- **SiPM_viewer_GUI.py**: Initialized UDP communication object alongside serial

### Files Added
- **Communication_lib/UDP_comm.py**: New UDP communication class

### UDP_comm Class
The `UDP_comm` class provides:
- `set_UDP_params(ip, port)`: Configure UDP parameters
- `UDP_connect()`: Bind to UDP socket and start listening
- `UDP_close()`: Close UDP socket
- `UDP_Receive_Start(queue)`: Start asynchronous UDP packet reception
- `UDP_Receive_Stop()`: Stop UDP reception
- `is_open()`: Check if UDP connection is active

### Message Processing
UDP packets are processed through the same pipeline as serial packets:
1. Raw bytes received via UDP socket
2. Validated using CRC8 checksum
3. Parsed into SerialMessage objects
4. Queued for processing
5. Handled by existing message handlers (measurements, control messages, etc.)

## Technical Notes
- UDP reception uses a 1-second timeout to check for stop events
- Multiple 7-byte packets can be received in a single UDP datagram
- The same message validation and CRC checking applies to UDP packets
- UDP uses the same histogram and data storage mechanisms as serial

## Default Configuration
- **UDP IP**: 0.0.0.0 (listen on all network interfaces)
- **UDP Port**: 5005
- **Packet Size**: 7 bytes
- **Socket Timeout**: 1 second
