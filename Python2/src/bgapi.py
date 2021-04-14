#!/usr/bin/env python

# Nathan Rhoades 10/13/2017 (modified from Jeff Rowberg's work)

import platform
import math
import bglib
import serial
import time
import datetime
import optparse
import signal
import sys
import struct


class Bluegiga():

    def __init__(self, dcb, ser, debugprint=False):

        self.dcb = dcb
        self.ser = ser
        self.debugprint = debugprint

        while True:
            reload(bglib)
            self.initialize()
            self.main_loop()

    def initialize(self):

        self.ble = 0
        self.peripheral_list = []
        self.connection_handle = 0
        self.att_handle_start = 0
        self.att_handle_end = 0
        self.att_handle_data = 0
        self.att_handle_data_ccc = 0
        self.crp_link_ready = False
        self.pending_write = False
        self.disconnected = 0
        self.connection_type = None
        self.connection_count = None
        self.connection_count_last = None
        self.mcu_data = None
        self.init_sent = False
        self.read_data = ""
        self.remoteAddressString = ""
        self.my_timeout = None

        self.uuid_service = [0x28, 0x00]  # 0x2800
        self.uuid_client_characteristic_configuration = [0x29, 0x02]  # 0x2902

        self.uuid_crp_service = [
            0x0b,
            0xd5,
            0x16,
            0x66,
            0xe7,
            0xcb,
            0x46,
            0x9b,
            0x8e,
            0x4d,
            0x27,
            0x42,
            0xf1,
            0xba,
            0x77,
            0xcc]
        self.uuid_crp_characteristic = [
            0xe7,
            0xad,
            0xd7,
            0x80,
            0xb0,
            0x42,
            0x48,
            0x76,
            0xaa,
            0xe1,
            0x11,
            0x28,
            0x55,
            0x35,
            0x3c,
            0xc1]

        self.STATE_STANDBY = 0
        self.STATE_CONNECTING = 1
        self.STATE_FINDING_SERVICES = 2
        self.STATE_FINDING_ATTRIBUTES = 3
        self.STATE_LISTENING_DATA = 4
        self.state = self.STATE_STANDBY

    def dprint(self, prnt):
        if self.debugprint:
            print "%s: %s" % (datetime.datetime.now().time(), prnt)

    # handler to notify of an API parser timeout condition
    def my_timeout(self, sender, args):
        # might want to try the following lines to reset, though it probably
        # wouldn't work at this point if it's already timed out:
        #ble.send_command(ser, self.ble.ble_cmd_system_reset(0))
        #ble.check_activity(ser, 1)
        self.dprint(
            "BGAPI parser timed out. Make sure the BLE device is in a known/idle state.")

    # gap_scan_response handler
    def my_ble_evt_gap_scan_response(self, sender, args):

        # pull all advertised service info from ad packet
        ad_services = []
        this_field = []
        bytes_left = 0
        for b in args['data']:
            if bytes_left == 0:
                bytes_left = b
                this_field = []
            else:
                this_field.append(b)
                bytes_left = bytes_left - 1
                if bytes_left == 0:
                    # partial or complete list of 16-bit UUIDs
                    if this_field[0] == 0x02 or this_field[0] == 0x03:
                        for i in xrange((len(this_field) - 1) / 2):
                            ad_services.append(
                                this_field[-1 - i * 2: -3 - i * 2: -1])
                    # partial or complete list of 32-bit UUIDs
                    if this_field[0] == 0x04 or this_field[0] == 0x05:
                        for i in xrange((len(this_field) - 1) / 4):
                            ad_services.append(
                                this_field[-1 - i * 4: -5 - i * 4: -1])
                    # partial or complete list of 128-bit UUIDs
                    if this_field[0] == 0x06 or this_field[0] == 0x07:
                        for i in xrange((len(this_field) - 1) / 16):
                            ad_services.append(
                                this_field[-1 - i * 16: -17 - i * 16: -1])

        # check for packets

        if self.uuid_crp_service in ad_services:
            # Attempt to connect for configuration reception
            if not args['sender'] in self.peripheral_list:
                self.peripheral_list.append(args['sender'])

                # connect to this device
                self.ble.send_command(self.ser, self.ble.ble_cmd_gap_connect_direct(
                    args['sender'], args['address_type'], 0x06, 0x10, 0x100, 0))
                self.ble.check_activity(self.ser, 1)
                self.state = self.STATE_CONNECTING
        else:
            self.dcb.receive(args['sender'], args['data'])

    # connection_status handler
    def my_ble_evt_connection_status(self, sender, args):

        if (args['flags'] & 0x05) == 0x05:
            # connected, now perform service discovery
            self.remoteAddressString = ':'.join(
                ['%02X' % b for b in args['address'][::-1]])
            self.dprint("Connected to %s" % self.remoteAddressString)
            self.connection_handle = args['connection']
            self.ble.send_command(self.ser, self.ble.ble_cmd_attclient_read_by_group_type(
                args['connection'], 0x0001, 0xFFFF, list(reversed(self.uuid_service))))
            self.ble.check_activity(self.ser, 1)
            self.state = self.STATE_FINDING_SERVICES

    # attclient_group_found handler
    def my_ble_evt_attclient_group_found(self, sender, args):

        # found "service" attribute groups (UUID=0x2800), check for CRP service
        if args['uuid'] == list(reversed(self.uuid_crp_service)):
            self.dprint(
                "Found attribute group for CRP service: start=%d, end=%d" %
                (args['start'], args['end']))
            self.att_handle_start = args['start']
            self.att_handle_end = args['end']

    # attclient_find_information_found handler
    def my_ble_evt_attclient_find_information_found(self, sender, args):

        # check for CRP data characteristic
        if args['uuid'] == list(reversed(self.uuid_crp_characteristic)):
            self.dprint(
                "Found CRP data attribute: handle=%d" %
                args['chrhandle'])
            self.att_handle_data = args['chrhandle']

        # check for subsequent client characteristic configuration
        elif args['uuid'] == list(reversed(self.uuid_client_characteristic_configuration)) and self.att_handle_data > 0:
            self.dprint(
                "Found CRP client characteristic config attribute w/UUID=0x2902: handle=%d" %
                args['chrhandle'])
            self.att_handle_data_ccc = args['chrhandle']

    # attclient_procedure_completed handler
    def my_ble_evt_attclient_procedure_completed(self, sender, args):

        # check if we just finished searching for services
        if self.state == self.STATE_FINDING_SERVICES:
            if self.att_handle_end > 0:
                self.dprint("Found CRP service")

                # found the Cable Replacement service, so now search for the
                # attributes inside
                self.state = self.STATE_FINDING_ATTRIBUTES
                self.ble.send_command(self.ser, self.ble.ble_cmd_attclient_find_information(
                    self.connection_handle, self.att_handle_start, self.att_handle_end))
                self.ble.check_activity(self.ser, 1)
            else:
                self.dprint("Could not find CRP service")

        # check if we just finished searching for attributes within the CRP
        # service
        elif self.state == self.STATE_FINDING_ATTRIBUTES:
            if self.att_handle_data_ccc > 0:
                self.dprint("Found CRP data attribute")

                # found the data + client characteristic configuration, so enable indications
                # (this is done by writing 0x0002 to the client characteristic configuration attribute)
                self.state = self.STATE_LISTENING_DATA
                self.ble.send_command(self.ser, self.ble.ble_cmd_attclient_attribute_write(
                    self.connection_handle, self.att_handle_data_ccc, [0x02, 0x00]))
                self.ble.check_activity(self.ser, 1)

                # note that the link is ready
                self.crp_link_ready = True
            else:
                self.dprint("Could not find CRP data attribute")

        # check for "write" acknowledgement if we just sent data
        elif self.state == self.STATE_LISTENING_DATA and args['chrhandle'] == self.att_handle_data:
            # clear "write" pending flag so we can send more data
            self.dprint("Configuration change verified by DigiCue Blue")
            self.pending_write = False

    # attclient_attribute_value handler
    def my_ble_evt_attclient_attribute_value(self, sender, args):

        # check for a new value from the connected peripheral's CRP data
        # attribute
        if args['connection'] == self.connection_handle and args['atthandle'] == self.att_handle_data:
            #sys.stdout.write(''.join(['%c' % b for b in args['value']]))
            read_data += ''.join(['%c' % b for b in args['value']])

    def my_ble_evt_connection_disconnected(self, connection, reason):

        self.dprint("Disconnected")
        self.disconnected = 1

    def main_loop(self):

        # create and setup BGLib object
        self.ble = bglib.BGLib()
        self.ble.packet_mode = False
        self.ble.debug = False

        # add handler for BGAPI timeout condition (hopefully won't happen)
        self.ble.on_timeout += self.my_timeout

        # add handlers for BGAPI events
        self.ble.ble_evt_gap_scan_response += self.my_ble_evt_gap_scan_response
        self.ble.ble_evt_connection_status += self.my_ble_evt_connection_status
        self.ble.ble_evt_attclient_group_found += self.my_ble_evt_attclient_group_found
        self.ble.ble_evt_attclient_find_information_found += self.my_ble_evt_attclient_find_information_found
        self.ble.ble_evt_attclient_procedure_completed += self.my_ble_evt_attclient_procedure_completed
        self.ble.ble_evt_attclient_attribute_value += self.my_ble_evt_attclient_attribute_value
        self.ble.ble_evt_connection_disconnected += self.my_ble_evt_connection_disconnected

        # flush buffers
        self.ser.flushInput()
        self.ser.flushOutput()

        # print address
        self.ble.send_command(self.ser, self.ble.ble_cmd_system_address_get())
        self.ble.check_activity(self.ser, 1)

        # disconnect if we are connected already
        self.ble.send_command(
            self.ser, self.ble.ble_cmd_connection_disconnect(0))
        self.ble.check_activity(self.ser, 1)

        # stop advertising if we are advertising already
        self.ble.send_command(self.ser, self.ble.ble_cmd_gap_set_mode(0, 0))
        self.ble.check_activity(self.ser, 1)

        # stop scanning if we are scanning already
        self.ble.send_command(self.ser, self.ble.ble_cmd_gap_end_procedure())
        self.ble.check_activity(self.ser, 1)

        # set scan parameters
        self.ble.send_command(
            self.ser, self.ble.ble_cmd_gap_set_scan_parameters(
                0xC8, 0xC8, 1))
        self.ble.check_activity(self.ser, 1)

        # start scanning now
        self.dprint("Scanning for DigiCue Blue")
        self.ble.send_command(self.ser, self.ble.ble_cmd_gap_discover(1))
        self.ble.check_activity(self.ser, 1)

        init_byte_sent = False
        while (self.disconnected == 0):

            # check for all incoming data (no timeout, non-blocking)
            self.ble.check_activity(self.ser)

            # don't burden the CPU
            time.sleep(0.01)

            if self.crp_link_ready and not self.pending_write:

                if not self.init_sent and self.dcb.pendACONF0 is not None:
                    # send configuration data (16 bytes)
                    self.init_sent = True
                    configuration_data = [
                        self.dcb.pendACONF0,
                        self.dcb.pendACONF1,
                        self.dcb.pendACONF2,
                        self.dcb.pendACONF3]
                    chksum = 0
                    for i in configuration_data:
                        chksum += i
                    chksum &= 0xff
                    configuration_data.append(chksum)
                    self.dprint("Connected")
                    self.ble.send_command(self.ser, self.ble.ble_cmd_attclient_attribute_write(
                        self.connection_handle, self.att_handle_data, configuration_data))
                    self.pending_write = True
