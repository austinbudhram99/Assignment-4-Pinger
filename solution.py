from array import array
from socket import *
import os
import sys
import struct
import time
import select
import binascii
from types import CodeType
from typing import Sequence
import statistics
# Should use stdev
packet_min = 999999999
packet_avg = 0
packet_max = 0
stdev_var = 0
timeRTT = []
packageRev = 0
packageSent = 0
stdev = 0

ICMP_ECHO_REQUEST = 8


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        ICMP_HEADER = recPacket[20:28]
        ICMP_Type, ICMP_CodeType, ICMP_Checksum, ICMP_ID, ICMP_Sequence = struct.unpack("bbHHh", ICMP_HEADER)
        
        if ICMP_ID == ID:
            ICMP_Bytes = struct.calcsize('d')
            timeMark = struct.unpack('d',recPacket[28:28 + ICMP_Bytes])
            ICMP_SentTime = timeMark[0]
            return timeReceived - ICMP_SentTime
        # Fetch the ICMP header from the IP packet

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them
    # vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str((round(stdev_var), 2))]
    # Send ping requests to a server separated by approximately one second
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        # list = []
        #timeRTT.append(round(delay[0]*1000,2))
        print(delay)
        #list.append(round(delay[0]*1000,2))
        time.sleep(1)  # one second
    # stdev = 0
    # delay = [0]
    #packet_min = min(delay)
    #packet_max = max(delay)
    #packet_avg = ((sum(delay))/((len(delay))))
    delay = list()
    delay.append((delay))
    #stdev_var = [0,1,2,3,4]
    #vars = [float(round(packet_min)), float(round(packet_avg)), float(round(packet_max)), float(round(stdev(stdev_var)))]
    #vars = [float(round(packet_min,2)), float(round(packet_avg,2)), float(round(packet_max,2)), float(round(statistics.stdev(stdev_var,2)))]
    #for i in lst:
      #  stdev += (i-packet_avg)**2
        # print (stdev)
    # stdev_var = math.sqrt((stdev / len(list)))
    # stdev_var = list(map(int, list))
    # vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
    return vars
    # print (vars)

if __name__ == '__main__':
    ping("google.co.il")
    ping("127.0.0.1")
