#!/usr/bin/env python3
"""
UDP Packet Sender - Test Script

This script sends test packets to the UDP receiver in the SiPM GUI.
It demonstrates the packet format and can be used for testing.

Usage:
    python3 udp_test_sender.py [target_ip] [target_port]

Example:
    python3 udp_test_sender.py 127.0.0.1 5005
"""

import socket
import time
import numpy as np

# CRC table (same as in SerialMessage.py)
crc_table = np.array([
    0,   49,  98,  83,  196, 245, 166, 151, 185, 136, 219, 234, 125, 76,  31,  46,
    67,  114, 33,  16,  135, 182, 229, 212, 250, 203, 152, 169, 62,  15,  92,  109,
    134, 183, 228, 213, 66,  115, 32,  17,  63,  14,  93,  108, 251, 202, 153, 168,
    197, 244, 167, 150, 1,   48,  99,  82,  124, 77,  30,  47,  184, 137, 218, 235,
    61,  12,  95,  110, 249, 200, 155, 170, 132, 181, 230, 215, 64,  113, 34,  19,
    126, 79,  28,  45,  186, 139, 216, 233, 199, 246, 165, 148, 3,   50,  97,  80,
    187, 138, 217, 232, 127, 78,  29,  44,  2,   51,  96,  81,  198, 247, 164, 149,
    248, 201, 154, 171, 60,  13,  94,  111, 65,  112, 35,  18,  133, 180, 231, 214,
    122, 75,  24,  41,  190, 143, 220, 237, 195, 242, 161, 144, 7,   54,  101, 84,
    57,  8,   91,  106, 253, 204, 159, 174, 128, 177, 226, 211, 68,  117, 38,  23,
    252, 205, 158, 175, 56,  9,   90,  107, 69,  116, 39,  22,  129, 176, 227, 210,
    191, 142, 221, 236, 123, 74,  25,  40,  6,   55,  100, 85,  194, 243, 160, 145,
    71,  118, 37,  20,  131, 178, 225, 208, 254, 207, 156, 173, 58,  11,  88,  105,
    4,   53,  102, 87,  192, 241, 162, 147, 189, 140, 223, 238, 121, 72,  27,  42,
    193, 240, 163, 146, 5,   52,  103, 86,  120, 73,  26,  43,  188, 141, 222, 239,
    130, 179, 224, 209, 70,  119, 36,  21,  59,  10,  89,  104, 255, 206, 157, 172
], np.uint8)

def calculate_crc8(header, data):
    """Calculate CRC8 for packet"""
    crc = 0
    crc = crc_table[crc ^ header]
    for byte in data:
        crc = crc_table[crc ^ byte]
    return crc

def build_packet(header, data):
    """
    Build a 7-byte packet
    
    Args:
        header: Message ID (1 byte)
        data: 4 bytes of data as list/array
    
    Returns:
        bytes: 7-byte packet
    """
    start_symbol = 0x55
    crc = calculate_crc8(header, data)
    
    packet = bytes([start_symbol, header, data[0], data[1], data[2], data[3], crc])
    return packet

def send_test_packets(target_ip, target_port, num_packets=10):
    """Send test packets via UDP"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Sending {num_packets} test packets to {target_ip}:{target_port}")
    
    for i in range(num_packets):
        # Create a test measurement packet (header = 3 = measured_pulse_val)
        # Value increases with each packet for testing
        value = 1000 + i * 100
        
        # Convert value to 4 bytes (little endian)
        data = [
            value & 0xFF,
            (value >> 8) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 24) & 0xFF
        ]
        
        packet = build_packet(3, data)  # Header 3 = measured_pulse_val
        
        sock.sendto(packet, (target_ip, target_port))
        print(f"Sent packet {i+1}: value={value}, bytes={packet.hex()}")
        
        time.sleep(0.5)  # Wait 500ms between packets
    
    sock.close()
    print("Done sending packets")

def send_heartbeat(target_ip, target_port):
    """Send a heartbeat packet"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Heartbeat packet (header = 4)
    data = [0, 0, 0, 1]  # Last byte indicates measurement running
    packet = build_packet(4, data)
    
    sock.sendto(packet, (target_ip, target_port))
    print(f"Sent heartbeat to {target_ip}:{target_port}")
    
    sock.close()

if __name__ == "__main__":
    import sys
    
    # Default values
    target_ip = "127.0.0.1"
    target_port = 5005
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    if len(sys.argv) > 2:
        target_port = int(sys.argv[2])
    
    print("="*50)
    print("UDP Packet Sender - Test Script")
    print("="*50)
    print()
    
    # Send test packets
    send_test_packets(target_ip, target_port, 10)
    
    print()
    print("Test complete!")
    print()
    print("Expected behavior in GUI:")
    print("- Connection status should show 'Device running'")
    print("- Histogram should update with measurement values")
    print("- Values should range from 1000 to 1900")
