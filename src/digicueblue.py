# Nathan Rhoades 10/13/2017

import math
import struct
import datetime
import math
import os


def toHex(x): return " ".join([hex(ord(c))[2:].zfill(2) for c in x])


class DigicueBlue():

    ACONF0 = None
    ACONF1 = None
    ACONF2 = None
    ACONF3 = None

    pendACONF0 = None
    pendACONF1 = None
    pendACONF2 = None
    pendACONF3 = None

    ALERT0 = None
    ALERT1 = None

    version = None

    macaddr = None
    macaddr_filter = None

    packet_count = None
    data = None
    data_type = None
    config = None
    setting = None
    alert = None
    payload = None

    impactmag = None
    impactang = None
    freezemag = None
    freezeang = None
    shottime = None
    bspause = None

    impactx = None
    impacty = None

    alert_shotpause = None
    alert_bspause = None
    alert_jab = None
    alert_followthru = None
    alert_steering = None
    alert_steering_right = None
    alert_steering_left = None
    alert_straightness = None
    alert_power = None
    alert_freeze = None

    score_shotpause = None
    score_bspause = None
    score_jab = None
    score_followthru = None
    score_steering = None
    score_steering = None
    score_straightness = None
    score_power = None
    score_freeze = None
    score_steering_direction = None

    threshset_shotpause = None
    threshset_bspause = None
    threshset_jab = None
    threshset_followthru = None
    threshset_steering = None
    threshset_straightness = None
    threshset_power = None
    threshset_freeze = None

    setting_shotpause = None
    setting_bspause = None
    setting_jab = None
    setting_followthru = None
    setting_steering = None
    setting_straightness = None
    setting_power = None
    setting_freeze = None

    setting_vop = None
    setting_dvibe = None

    threshold_shotpause = None
    threshold_bspause = None
    threshold_jab = None
    threshold_followthru = None
    threshold_steering = None
    threshold_straightness = None
    threshold_power = None
    threshold_freeze = None

    file_date = []
    file_shotpause = []
    file_bspause = []
    file_jab = []
    file_followthru = []
    file_steering = []
    file_steering_direction = []
    file_straightness = []
    file_power = []
    file_freeze = []
    file_impactx = []
    file_impacty = []

    config_options = [
        ("Shot Interval", (("5s", 0), ("8s", 1), ("12s", 2), ("15s", 3))),
        ("Backstroke Pause", (("0.1s", 0), ("0.2s", 1), ("0.5s", 2), ("1s", 3))),
        ("Jab", (("Low", 3), ("Medium", 2), ("High", 1), ("Extreme", 0))),
        ("Follow Through", (("Very Punchy", 0), ("Punchy", 1), ("Smooth", 2), ("Very Smooth", 3))),
        ("Tip Steer", (("Low", 0), ("Medium", 1), ("High", 2), ("Extreme", 3))),
        ("Straightness", (("Low", 3), ("Medium", 2), ("High", 1), ("Extreme", 0))),
        ("Finesse", (("Very Soft", 0), ("Soft", 1), ("Medium Soft", 2), ("Medium", 3))),
        ("Finish", (("1s", 0), ("1.5s", 1), ("2s", 2), ("2.5s", 3))),
        ("Vibrate On Pass", (("Off", 0), ("On", 1))),
        ("Disable All Vibrations", (("Off", 0), ("On", 1))),
    ]

    def set_config(self, configuration):

        setting = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        thresh = [0, 0, 0, 0, 0, 0, 0, 0]

        tmp = int(configuration["Shot Interval"])
        setting[0] = 1 if tmp > -1 else 0
        thresh[0] = tmp if tmp > -1 else 0

        tmp = int(configuration["Backstroke Pause"])
        setting[1] = 1 if tmp > -1 else 0
        thresh[1] = tmp if tmp > -1 else 0

        tmp = int(configuration["Jab"])
        setting[2] = 1 if tmp > -1 else 0
        thresh[2] = tmp if tmp > -1 else 0

        tmp = int(configuration["Follow Through"])
        setting[3] = 1 if tmp > -1 else 0
        thresh[3] = tmp if tmp > -1 else 0

        tmp = int(configuration["Tip Steer"])
        setting[4] = 1 if tmp > -1 else 0
        thresh[4] = tmp if tmp > -1 else 0

        tmp = int(configuration["Straightness"])
        setting[5] = 1 if tmp > -1 else 0
        thresh[5] = tmp if tmp > -1 else 0

        tmp = int(configuration["Finesse"])
        setting[6] = 1 if tmp > -1 else 0
        thresh[7] = tmp if tmp > -1 else 0

        tmp = int(configuration["Finish"])
        setting[7] = 1 if tmp > -1 else 0
        thresh[7] = tmp if tmp > -1 else 0

        tmp = int(configuration["Vibrate On Pass"])
        setting[8] = 1 if tmp > -1 else 0

        tmp = int(configuration["Disable All Vibrations"])
        setting[9] = 1 if tmp > -1 else 0

        self.pendACONF0 = (
            setting[7] << 7) | (
            setting[6] << 6) | (
            setting[5] << 5) | (
                setting[4] << 4) | (
                    setting[3] << 3) | (
                        setting[2] << 2) | (
                            setting[1] << 1) | setting[0]
        self.pendACONF1 = (
            (thresh[3] & 0x03) << 6) | (
            (thresh[2] & 0x03) << 4) | (
            (thresh[1] & 0x03) << 2) | (
                thresh[0] & 0x03)
        self.pendACONF2 = (
            (thresh[7] & 0x03) << 6) | (
            (thresh[6] & 0x03) << 4) | (
            (thresh[5] & 0x03) << 2) | (
                thresh[4] & 0x03)
        self.pendACONF3 = ((setting[9] & 1) << 1) | (setting[8] & 1)

    def __init__(self, filename=None, debugprint=False):
        self.filename = filename
        self.debugprint = debugprint

    def dprint(self, prnt):
        if self.debugprint:
            print "%s (%i): %s" % (datetime.datetime.now().time(), self.packet_count, prnt)

    def file_import(self, datefrom=None, dateto=None, macaddr=None):

        file = open(self.filename, "r")
        linenum = 0

        while True:
            line = file.readline()
            if not line:
                break
            linenum += 1
            parse = line.rstrip().split(',')
            date = datetime.datetime.strptime(parse[0], "%Y-%m-%d %H:%M:%S.%f")
            macaddr = parse[1]

            append = True

            if dateto is not None:
                if date > dateto:
                    break

            if datefrom is not None:
                if date >= datefrom:
                    append = False

            if append:
                self.file_date.append(date)
                self.file_shotpause.append(float(parse[2]))
                self.file_bspause.append(float(parse[3]))
                self.file_jab.append(float(parse[4]))
                self.file_followthru.append(float(parse[5]))
                self.file_steering.append(float(parse[6]))
                self.file_steering_direction.append(parse[7])
                self.file_straightness.append(float(parse[8]))
                self.file_power.append(float(parse[9]))
                self.file_freeze.append(float(parse[10]))
                self.file_impactx.append(float(parse[11]))
                self.file_impacty.append(float(parse[11]))

        file.close()

    def file_append(self):
        if self.filename is None:
            return

        exists = os.path.isfile(self.filename)
        file = open(self.filename, "a")
        if not exists:
            tmp = "Date,MAC,ShotInterval,BackstrokePause,Jab,FollowThrough,TipSteer,TipSteerDir,Straightness,Finesse,Finish,ImpactX,ImpactY\n"
            file.write(tmp)

        textstr = "%s" % (str(datetime.datetime.now()))
        textstr += ",%s" % self.macaddr
        textstr += ",%.2f" % self.score_shotpause
        textstr += ",%.2f" % self.score_bspause
        textstr += ",%.2f" % self.score_jab
        textstr += ",%.2f" % self.score_followthru
        textstr += ",%.2f" % self.score_steering
        textstr += ",%s" % self.score_steering_direction
        textstr += ",%.2f" % self.score_straightness
        textstr += ",%.2f" % self.score_power
        textstr += ",%.2f" % self.score_freeze
        textstr += ",%.2f" % self.impactx
        textstr += ",%.2f" % self.impacty
        textstr += "\n"

        file.write(textstr)

        if file is not None:
            file.close()

    def debug_print(self):
        if not self.debugprint:
            return
        print ''
        print "Packet Data:"
        print self.data
        self.dprint('ACONF0: %r' % self.ACONF0)
        self.dprint('ACONF1: %r' % self.ACONF1)
        self.dprint('ACONF2: %r' % self.ACONF2)
        self.dprint('ACONF3: %r' % self.ACONF3)
        self.dprint('ALERT0: %r' % self.ALERT0)
        self.dprint('ALERT1: %r' % self.ALERT1)
        self.dprint('version: %r' % self.version)
        self.dprint('packet_count: %r' % self.packet_count)
        self.dprint('data_type: %r' % self.data_type)
        self.dprint('config: %r' % self.config)
        self.dprint('setting: %r' % self.setting)
        self.dprint('alert: %r' % self.alert)
        self.dprint('impactmag: %r' % self.impactmag)
        self.dprint('impactang: %r' % self.impactang)
        self.dprint('freezemag: %r' % self.freezemag)
        self.dprint('freezeang: %r' % self.freezeang)
        self.dprint('shottime: %r' % self.shottime)
        self.dprint('bspause: %r' % self.bspause)
        self.dprint('setting_shotpause: %r' % self.setting_shotpause)
        self.dprint('setting_bspause: %r' % self.setting_bspause)
        self.dprint('setting_jab: %r' % self.setting_jab)
        self.dprint('setting_followthru: %r' % self.setting_followthru)
        self.dprint('setting_steering: %r' % self.setting_steering)
        self.dprint('setting_straightness: %r' % self.setting_straightness)
        self.dprint('setting_power: %r' % self.setting_power)
        self.dprint('setting_freeze: %r' % self.setting_freeze)
        self.dprint('threshold_shotpause: %r' % self.threshold_shotpause)
        self.dprint('threshold_bspause: %r' % self.threshold_bspause)
        self.dprint('threshold_jab: %r' % self.threshold_jab)
        self.dprint('threshold_followthru: %r' % self.threshold_followthru)
        self.dprint('threshold_steering: %r' % self.threshold_steering)
        self.dprint('threshold_straightness: %r' % self.threshold_straightness)
        self.dprint('threshold_power: %r' % self.threshold_power)
        self.dprint('threshold_freeze: %r' % self.threshold_freeze)
        self.dprint('alert_shotpause: %r' % self.alert_shotpause)
        self.dprint('alert_bspause: %r' % self.alert_bspause)
        self.dprint('alert_jab: %r' % self.alert_jab)
        self.dprint('alert_followthru: %r' % self.alert_followthru)
        self.dprint('alert_steering_right: %r' % self.alert_steering_right)
        self.dprint('alert_steering_left: %r' % self.alert_steering_left)
        self.dprint('alert_straightness: %r' % self.alert_straightness)
        self.dprint('alert_power: %r' % self.alert_power)
        self.dprint('alert_freeze: %r' % self.alert_freeze)
        self.dprint('score_shotpause: %r' % self.score_shotpause)
        self.dprint('score_bspause: %r' % self.score_bspause)
        self.dprint('score_jab: %r' % self.score_jab)
        self.dprint('score_followthru: %r' % self.score_followthru)
        self.dprint('score_steering: %r' % self.score_steering)
        self.dprint('score_straightness: %r' % self.score_straightness)
        self.dprint('score_power: %r' % self.score_power)
        self.dprint('score_freeze: %r' % self.score_freeze)

    def format_mac_addr(self, mac):
        macaddr = mac
        macaddr.reverse()
        return (6 * "%.2X") % tuple(macaddr)

    def receive(self, mac, data):

        # Filter for minimum 14 bytes length
        if len(data) < 14:
            return

        # Filter for Nathan Rhoades LLC manufacturing header
        if data[0:3] != [0x02, 0x01, 0x06] or \
                        data[10] < 0x04 or \
                        data[11:14] != [0xFF, 0x03, 0xDE]:
            return

        # Set mac address
        self.macaddr = self.format_mac_addr(mac)
        if self.macaddr_filter != self.macaddr:
            return

        # Extract header and payload
        mcu_data_length = data[10] - 4
        mcu_data = data[14:]
        if mcu_data_length < 2:
            return
        config = mcu_data[1]
        data_type = (config >> 3) & 0x03
        setting = (config >> 1) & 0x03
        alert = config & 0x01
        payload = mcu_data[2:]

        # Ignore more than once instance of same packet
        if mcu_data[0] == self.packet_count:
            return
        self.packet_count = mcu_data[0]
        self.data = data
        self.data_type = data_type
        self.config = config
        self.setting = setting
        self.alert = alert
        self.payload = payload

        paybuffer = ""
        for c in payload:
            paybuffer += chr(c)

        aconf = struct.unpack('4B', paybuffer[:4])
        self.ACONF0, self.ACONF1, self.ACONF2, self.ACONF3 = aconf

        self.setting_shotpause = (self.ACONF0 >> 0) & 1
        self.setting_bspause = (self.ACONF0 >> 1) & 1
        self.setting_jab = (self.ACONF0 >> 2) & 1
        self.setting_followthru = (self.ACONF0 >> 3) & 1
        self.setting_steering = (self.ACONF0 >> 4) & 1
        self.setting_straightness = (self.ACONF0 >> 5) & 1
        self.setting_power = (self.ACONF0 >> 6) & 1
        self.setting_freeze = (self.ACONF0 >> 7) & 1
        self.setting_vop = self.ACONF3 & 1
        self.setting_dvibe = (self.ACONF3 >> 1) & 1

        self.threshset_shotpause = self.ACONF1 & 3
        self.threshset_bspause = (self.ACONF1 >> 2) & 3
        self.threshset_jab = (self.ACONF1 >> 4) & 3
        self.threshset_followthru = (self.ACONF1 >> 6) & 3
        self.threshset_steering = self.ACONF2 & 3
        self.threshset_straightness = (self.ACONF2 >> 2) & 3
        self.threshset_power = (self.ACONF2 >> 4) & 3
        self.threshset_freeze = (self.ACONF2 >> 6) & 3

        if data_type == 0:  # Version
            version = ''
            for c in payload[4:]:
                if c == 0:
                    break
                version += chr(c)
            self.version = version

        else:

            alert0, alert1 = struct.unpack('2B', paybuffer[4:6])
            self.ALERT0 = alert0
            self.ALERT1 = alert1

            shot_timer = struct.unpack('B', paybuffer[6])[0]
            pause_time = struct.unpack('B', paybuffer[7])[0]
            follow_thr = struct.unpack('B', paybuffer[8])[0]
            jabmag = struct.unpack('B', paybuffer[9])[0]
            impactang = struct.unpack('B', paybuffer[10])[0]
            impactmag = struct.unpack('B', paybuffer[11])[0]
            freezeang = struct.unpack('B', paybuffer[12])[0]
            freezetime = struct.unpack('B', paybuffer[13])[0]
            shotpower = struct.unpack('B', paybuffer[14])[0]
            freezemag = alert1 >> 1

            self.impactmag = impactmag
            impactang = impactang * 180 / 128.0
            if impactang < 0:
                impactang += 360
            self.impactang = impactang

            self.impactx = -impactmag * \
                math.cos(math.pi / 180 * impactang - math.pi / 2)
            self.impacty = -impactmag * \
                math.sin(math.pi / 180 * impactang - math.pi / 2)

            self.freezemag = freezemag
            freezeang = freezeang * 180 / 128.0
            if freezeang < 0:
                freezeang += 360
            self.freezeang = freezeang

            if shot_timer > 234:
                shot_time = 120.0
            else:
                shot_time = float(shot_timer * .512)
            self.shottime = shot_time

            if pause_time > 83:
                backstroke_pause = 1.0
            else:
                backstroke_pause = float(pause_time * 0.012)
            self.bspause = backstroke_pause
            self.score_bspause = backstroke_pause

            tmp = self.threshset_bspause
            if tmp == 0:
                self.threshold_bspause = 0.1
            elif tmp == 1:
                self.threshold_bspause = 0.2
            elif tmp == 2:
                self.threshold_bspause = 0.5
            else:
                self.threshold_bspause = 1.0

            tmp = jabmag
            if tmp > 125:
                tmp = 125
            self.score_jab = (125 - tmp) / 12.5
            tmp = self.threshset_jab
            if tmp == 0:
                self.threshold_jab = (125 - 25) / 12.5
            elif tmp == 1:
                self.threshold_jab = (125 - 50) / 12.5
            elif tmp == 2:
                self.threshold_jab = (125 - 75) / 12.5
            else:
                self.threshold_jab = (125 - 100) / 12.5

            self.score_followthru = follow_thr - 1
            tmp = self.threshset_followthru
            if tmp == 0:
                self.threshold_followthru = 4.0
            elif tmp == 1:
                self.threshold_followthru = 6.0
            elif tmp == 2:
                self.threshold_followthru = 8.0
            else:
                self.threshold_followthru = 10.0

            j = 0
            for k in xrange(0, 10):
                i = k * 85 / 9.0
                if (impactang > (90 - i) and impactang < (90 + i)
                    ) or (impactang > (270 - i) and impactang < (270 + i)):
                    break
                else:
                    j += 1
            if impactmag <= 10:
                j = 10
            self.score_steering = j
            tmp = self.threshset_steering
            if tmp == 0:
                self.threshold_steering = 2.0
            elif tmp == 1:
                self.threshold_steering = 4.0
            elif tmp == 2:
                self.threshold_steering = 6.0
            else:
                self.threshold_steering = 8.0

            self.score_steering_direction = "C"
            if self.impactmag > 10:
                if self.impactx > 0:
                    self.score_steering_direction = "R"
                else:
                    self.score_steering_direction = "L"

            tmp = impactmag
            if tmp > 50:
                tmp = 50
            tmp = (50 - tmp) / 5.0
            self.score_straightness = tmp
            tmp = self.threshset_straightness
            if tmp == 0:
                self.threshold_straightness = 9.0
            elif tmp == 1:
                self.threshold_straightness = 8.0
            elif tmp == 2:
                self.threshold_straightness = 6.0
            else:
                self.threshold_straightness = 3.0

            tmp = shotpower
            if tmp < 50:
                tmp = 50
            if tmp > 110:
                tmp = 110
            self.score_power = 10 - (10 * (tmp - 50.0) / (110 - 50.0))
            tmp = self.threshset_power
            if tmp == 0:
                self.threshold_power = 7.0
            elif tmp == 1:
                self.threshold_power = 5.0
            elif tmp == 2:
                self.threshold_power = 3.0
            else:
                self.threshold_power = 2.0

            self.score_freeze = (freezetime + 48) * 0.012
            tmp = self.threshset_freeze
            if tmp == 0:
                self.threshold_freeze = 1.0
            elif tmp == 1:
                self.threshold_freeze = 1.5
            elif tmp == 2:
                self.threshold_freeze = 2.0
            else:
                self.threshold_freeze = 2.5

            self.score_shotpause = self.shottime
            tmp = self.threshset_shotpause
            if tmp == 0:
                self.threshold_shotpause = 5.0
            elif tmp == 1:
                self.threshold_shotpause = 8.0
            elif tmp == 2:
                self.threshold_shotpause = 12.0
            else:
                self.threshold_shotpause = 15.0

            self.alert_shotpause = (alert0 >> 0) & 1
            self.alert_bspause = (alert0 >> 1) & 1
            self.alert_jab = (alert0 >> 2) & 1
            self.alert_followthru = (alert0 >> 3) & 1
            self.alert_steering = (alert0 >> 4) & 1
            if self.alert_steering:
                self.alert_steering_right = (alert1 & 1)
                self.alert_steering_left = not (alert1 & 1)
            else:
                self.alert_steering_right = None
                self.alert_steering_left = None
            self.alert_straightness = (alert0 >> 5) & 1
            self.alert_power = (alert0 >> 6) & 1
            self.alert_freeze = (alert0 >> 7) & 1

            self.file_append()

        self.debug_print()
