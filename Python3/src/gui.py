# Nathan Rhoades 10/13/2017

VERSION = "1.0.0"

import sys
import random
import helptext
import tkinter as Tk
from tkinter import ttk

class Resizable():
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas_width_orig = canvas.width
        self.canvas_height_orig = canvas.height

    def redraw(self, x0, y0, x1, y1, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = x0 * self.ratio_width
        b = y0 * self.ratio_height
        c = x1 * self.ratio_width
        d = y1 * self.ratio_height
        self.canvas.coords(self.object, a, b, c, d, **kwargs)

    def itemconfig(self, **kwargs):
        self.canvas.itemconfig(self.object, **kwargs)


class ResizablePlotPoint(Resizable):
    def __init__(self, canvas, x0, y0, mag, **kwargs):
        Resizable.__init__(self, canvas)
        self.x0 = x0
        self.y0 = y0
        self.mag = mag
        self.size = 3
        self.object = canvas.create_oval(
            x0 - self.size,
            y0 - self.size,
            x0 + self.size,
            y0 + self.size,
            **kwargs)

    def redraw(self, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = self.x0 * self.ratio_width
        b = self.y0 * self.ratio_height
        self.canvas.coords(
            self.object,
            a - self.size,
            b - self.size,
            a + self.size,
            b + self.size,
            **kwargs)


class ResizableRectangle(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_rectangle(x0, y0, x1, y1, **kwargs)


class ResizableLine(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_line(x0, y0, x1, y1, **kwargs)


class ResizableOval(Resizable):
    def __init__(self, canvas, x0, y0, x1, y1, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_oval(x0, y0, x1, y1, **kwargs)


class ResizableText(Resizable):
    def __init__(self, canvas, x0, y0, **kwargs):
        Resizable.__init__(self, canvas)
        self.object = canvas.create_text(x0, y0, **kwargs)

    def redraw(self, x0, y0, **kwargs):
        self.ratio_width = self.canvas.width / float(self.canvas_width_orig)
        self.ratio_height = self.canvas.height / float(self.canvas_height_orig)
        a = x0 * self.ratio_width
        b = y0 * self.ratio_height
        self.canvas.coords(self.object, a, b, **kwargs)


class ResizableCanvas(Tk.Canvas):
    def __init__(self, parent, **kwargs):
        Tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)


class ScoreBar:
    def __init__(self, canvas, left, top, right, bottom, scale):
        self.canvas = canvas
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.scale = scale

        self.score = 0.0
        self.threshold = 0.0
        self.average = 0.0
        self.points = 0.0

        self.scorebar = ResizableRectangle(
            canvas, 0, 0, 0, 0, fill="red", outline="")
        self.avgbar = ResizableRectangle(
            canvas, 0, 0, 0, 0, fill="dark gray", outline="")
        self.thresholdline = ResizableLine(canvas, 0, 0, 0, 0)

        ResizableRectangle(canvas, left, top, right, bottom)

    def update(self, enabled=True):
        self.points += 1
        if self.points == 1:
            self.average = self.score
        else:
            self.average = self.average * \
                (self.points - 1) / float(self.points) + self.score / float(self.points)

        score = self.score
        threshold = self.threshold
        average = self.average
        if average < 0:
            average = 0
        elif average > self.scale:
            average = self.scale
        if score < 0:
            score = 0
        elif score > self.scale:
            score = self.scale
        if threshold < 0:
            threshold = 0
        elif threshold > self.scale:
            threshold = self.scale

        mid = self.left + (self.right - self.left) * score / self.scale
        avg = self.left + (self.right - self.left) * average / self.scale
        if enabled:
            thresh = self.left + (self.right - self.left) * threshold / self.scale
        else:
            thresh = self.left

        if enabled:
            if mid >= thresh:
                color = "green"
            else:
                color = "red"
        else:
            color = "gray"

        self.scorebar.itemconfig(fill=color)
        self.scorebar.redraw(self.left, self.top, mid, self.bottom)
        self.avgbar.redraw(self.left, self.bottom, avg,
                            self.bottom + (self.bottom - self.top) * 0.25)
        self.thresholdline.redraw(
            thresh, self.top, thresh, self.bottom)


class Plot:

    def __init__(self, canvas, left, top, size):
        self.canvas = canvas
        self.canvas_width_orig = canvas.width
        self.canvas_height_orig = canvas.height
        self.left = left
        self.top = top
        self.size = size
        self.points = []

        ResizableRectangle(
            self.canvas,
            self.left,
            self.top,
            self.left +
            self.size,
            self.top +
            self.size)
        ResizableLine(
            self.canvas,
            self.left,
            self.top + self.size / 2,
            self.left + self.size,
            self.top + self.size / 2)
        ResizableLine(
            self.canvas,
            self.left + self.size / 2,
            self.top,
            self.left + self.size / 2,
            self.top + self.size)

        # Make circles at 35,20,10,5 (thresholds for straightness)
        x0 = self.left + self.size / 2
        y0 = self.top + self.size / 2
        self.x0 = x0
        self.y0 = y0
        r = 0.5
        self.threshold_circle = ResizableOval(
            self.canvas, x0 - r, y0 - r, x0 + r, y0 + r)

    def plot(self, x, y, **kwargs):
        # Plots point in plot area. Limits are -1 to 1
        if x > 1:
            x = 1.
        if y > 1:
            y = 1.
        if x < -1:
            x = -1.
        if y < -1:
            y = -1.
        mag = (x**2 + y**2)**0.5
        x = (x * self.size / 2 + self.x0) * self.canvas.width / (float(self.canvas_width_orig))
        y = (y * self.size / 2 + self.y0) * self.canvas.height / (float(self.canvas_height_orig))
        self.points.append(
            ResizablePlotPoint(
                self.canvas, x, y, mag, **kwargs))

    def update(self, threshold):
        self.threshold = threshold
        r = threshold * self.size / 2
        self.threshold_circle.redraw(
            self.x0 - r, self.y0 - r, self.x0 + r, self.y0 + r)
        for i in range(0, len(self.points)):
            point = self.points[i]
            if i == (len(self.points) - 1):
                if point.mag > self.threshold:
                    color = "red"
                else:
                    color = "green"
            else:
                color = "dark gray"
            point.itemconfig(fill=color)
            point.redraw()


class ScoreBars:

    def __init__(self, frame, dcb):

        self.dcb = dcb
        self.frame = frame

        self.canvas = ResizableCanvas(
            self.frame,
            width=810,
            height=400,
            highlightthickness=0)
        self.canvas.pack(fill=Tk.BOTH, expand=Tk.YES)

        left = 300
        right = 550
        self.bars = []
        self.scores = []
        self.labels = (
            'Finish',
            'Finesse',
            'Straightness',
            'Tip Steer',
            'Follow Through',
            'Jab',
            'Backstroke Pause',
            'Shot Interval')
        self.scale = (3.0, 10.0, 10.0, 10.0, 10.0, 10.0, 1.0, 60.0)
        self.score_format = (
            "%0.2fs",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.1f",
            "%0.2fs",
            "%0.1fs")
        self.outof = ('/3s', '/10', '/10', '/10', '/10', '/10', '/1s', '/60s')
        for i in range(0, 8):
            top = i * 400 / 8. + 10
            bottom = (i + 1) * 400 / 8. - 10
            self.bars.append(
                ScoreBar(
                    self.canvas,
                    left,
                    top,
                    right,
                    bottom,
                    self.scale[i]))
            ResizableRectangle(self.canvas, 10, top, left - 10, bottom)
            ResizableRectangle(self.canvas, left - 10, top, left - 100, bottom)
            ResizableText(self.canvas, 100, top + (bottom - top)
                          * 0.5, text=self.labels[i], font=("Purisa", 14))
            ResizableText(self.canvas, 575, top + (bottom - top)
                          * 0.5, text=self.outof[i], font=("Purisa", 14))
            self.scores.append(ResizableText(
                self.canvas, left - 55, top + (bottom - top) * 0.5, text="0", font=("Purisa", 18)))

        # Plot area
        self.plot = Plot(self.canvas, 600, 100, 200)
        ResizableText(
            self.canvas,
            700,
            75,
            text="Straightness",
            font=(
                "Purisa",
                14))

    def _update_scores(self):
        for i in range(0, 8):
            text = self.score_format[i] % self.bars[i].score
            self.scores[i].itemconfig(text=text)

    def test(self):

        for bar in self.bars:
            bar.average = bar.scale * random.random()
            bar.score = bar.scale * random.random()
            bar.threshold = bar.scale * random.random()
            bar.update(True)
        self._update_scores()
        x = random.normalvariate(0, 0.5)
        y = random.normalvariate(0, 0.5)
        self.plot.plot(x, y)
        self.plot.update(random.random())

    def update(self):
        dcb = self.dcb

        self.bars[0].score = dcb.score_freeze
        self.bars[0].threshold = dcb.threshold_freeze
        self.bars[0].update(dcb.setting_freeze)

        self.bars[1].score = dcb.score_power
        self.bars[1].threshold = dcb.threshold_power
        self.bars[1].update(dcb.setting_power)

        self.bars[2].score = dcb.score_straightness
        self.bars[2].threshold = dcb.threshold_straightness
        self.bars[2].update(dcb.setting_straightness)

        self.bars[3].score = dcb.score_steering
        self.bars[3].threshold = dcb.threshold_steering
        self.bars[3].update(dcb.setting_steering)

        self.bars[4].score = dcb.score_followthru
        self.bars[4].threshold = dcb.threshold_followthru
        self.bars[4].update(dcb.setting_followthru)

        self.bars[5].score = dcb.score_jab
        self.bars[5].threshold = dcb.threshold_jab
        self.bars[5].update(dcb.setting_jab)

        self.bars[6].score = dcb.score_bspause
        self.bars[6].threshold = dcb.threshold_bspause
        self.bars[6].update(dcb.setting_bspause)

        self.bars[7].score = dcb.score_shotpause
        self.bars[7].threshold = dcb.threshold_shotpause
        self.bars[7].update(dcb.setting_shotpause)

        self._update_scores()

        x = dcb.impactx / 50.
        y = dcb.impacty / 50.
        thresh = (50 - 5 * dcb.threshold_straightness) / 50.
        self.plot.plot(x, y)
        self.plot.update(thresh)


class OptionList_Command_MacAddr:

    def __init__(self, parent):
        self.parent = parent

    def set(self, value):  # run when option list is changed
        print("Selected MAC Address " + value)
        self.parent.macaddrs.set(value)
        self.parent.macaddr = value
        self.parent.dcb.macaddr_filter = value


class GUI:

    def __init__(self, master, dcb):

        # All variables from DigiCue Blue are exposed through class variables
        # in dcb

        self.dcb = dcb
        self.packet_count = dcb.packet_count
        self.master = master
        master.after(500, self.timer)  # register timer
        master.title("DigiCue Blue BLED112 GUI - Version %s" % VERSION)

        self.tabs = ttk.Notebook(master)
        self.tab1 = Tk.Frame(self.tabs, padx=10, pady=10)
        self.tab3 = Tk.Frame(self.tabs, padx=10, pady=10)
        self.tab5 = Tk.Frame(self.tabs, padx=10, pady=10)
        self.tabs.add(self.tab1, text='Shots')
        self.tabs.add(self.tab3, text='Configure')
        self.tabs.add(self.tab5, text='Help')
        self.tabs.pack(fill=Tk.BOTH, expand=Tk.YES)

        # Help tab
        message = helptext.help
        frame = Tk.Frame(self.tab5)
        text = Tk.Text(frame, height=30, width=100, wrap=Tk.WORD)
        text.insert(Tk.END, message)
        scroll = Tk.Scrollbar(frame)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=Tk.LEFT)
        scroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        frame.pack(side=Tk.TOP)
        text.config(state=Tk.DISABLED)

        # Mac addr select
        frame = Tk.Frame(self.tab3)
        frame.pack(fill=Tk.X)
        self.macaddr = None
        self.macaddrs_list = []
        self.macaddr_commands = []
        lbl = Tk.Label(frame, text="DigiCue Blue MAC Address", width=25)
        lbl.pack(side=Tk.LEFT)
        self.macaddrs = Tk.StringVar(frame)
        self.macaddrs.set("<Auto Detect>")
        self.macaddrs_combo = Tk.OptionMenu(
            frame, self.macaddrs, "<Auto Detect>")
        self.macaddrs_combo.pack(side=Tk.LEFT)

        # Configuration selection
        frame = Tk.Frame(self.tab3)
        frame.pack(fill=Tk.X)
        label = Tk.Label(frame, text="Configure")
        label.pack(side=Tk.LEFT)

        self.options_configig = {}
        fbox = Tk.Frame(self.tab3, relief=Tk.GROOVE, bd=2)
        fbox.pack(fill=Tk.X)
        for label, modes in dcb.config_options:
            frame = Tk.Frame(fbox)
            frame.pack(fill=Tk.X)
            lbl = Tk.Label(frame, text=label, width=25)
            lbl.pack(side=Tk.LEFT)
            v = Tk.StringVar()
            b = Tk.Radiobutton(
                frame,
                text="Off",
                variable=v,
                value=-1,
                indicatoron=0,
                width=10,
                command=self.check_setting_config)
            b.pack(side=Tk.LEFT)
            for text, mode in modes:
                if text != "Off":
                    b = Tk.Radiobutton(
                        frame,
                        text=text,
                        variable=v,
                        value=mode,
                        indicatoron=0,
                        width=10,
                        command=self.check_setting_config)
                    b.pack(side=Tk.LEFT)
            self.options_configig[label] = v
        frame = Tk.Frame(fbox, pady=10)
        frame.pack(fill=Tk.X)
        lbl = Tk.Label(frame, text="", width=25)
        lbl.pack(side=Tk.LEFT)
        self.sync_label = Tk.StringVar(frame)
        self.sync_label.set("Press button on DigiCue Blue once to detect")
        lbl = Tk.Label(frame, textvariable=self.sync_label)
        lbl.pack(side=Tk.LEFT)

        # Shots tab
        self.scorebars = ScoreBars(self.tab1, dcb)

    def refresh_setting_config(self):
        self.options_configig["Shot Interval"].set(
            self.dcb.threshset_shotpause if self.dcb.setting_shotpause else -1)
        self.options_configig["Backstroke Pause"].set(
            self.dcb.threshset_bspause if self.dcb.setting_bspause else -1)
        self.options_configig["Jab"].set(
            self.dcb.threshset_jab if self.dcb.setting_jab else -1)
        self.options_configig["Follow Through"].set(
            self.dcb.threshset_followthru if self.dcb.setting_followthru else -1)
        self.options_configig["Tip Steer"].set(
            self.dcb.threshset_steering if self.dcb.setting_steering else -1)
        self.options_configig["Straightness"].set(
            self.dcb.threshset_straightness if self.dcb.setting_straightness else -1)
        self.options_configig["Finesse"].set(
            self.dcb.threshset_power if self.dcb.setting_power else -1)
        self.options_configig["Finish"].set(
            self.dcb.threshset_freeze if self.dcb.setting_freeze else -1)
        self.options_configig["Vibrate On Pass"].set(
            self.dcb.setting_vop if self.dcb.setting_vop else -1)
        self.options_configig["Disable All Vibrations"].set(
            self.dcb.setting_dvibe if self.dcb.setting_dvibe else -1)
        self.check_setting_config()

    def check_setting_config(self):

        configuration = {}
        for key in self.options_configig:
            configuration[key] = self.options_configig[key].get()
        self.dcb.set_config(configuration)

        if not self.check_setting_config_test():
            self.sync_label.set("Press button on DigiCue Blue twice to sync")
        else:
            self.sync_label.set("Configuration matches DigiCue Blue")

    def check_setting_config_test(self):

        a = 0

        def val(x): return -2 if len(x) == 0 else x

        tmp = int(val(self.options_configig["Shot Interval"].get()))
        if self.dcb.setting_shotpause:
            a += int(tmp == self.dcb.threshset_shotpause)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Backstroke Pause"].get()))
        if self.dcb.setting_bspause:
            a += int(tmp == self.dcb.threshset_bspause)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Jab"].get()))
        if self.dcb.setting_jab:
            a += int(tmp == self.dcb.threshset_jab)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Follow Through"].get()))
        if self.dcb.setting_followthru:
            a += int(tmp == self.dcb.threshset_followthru)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Tip Steer"].get()))
        if self.dcb.setting_steering:
            a += int(tmp == self.dcb.threshset_steering)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Straightness"].get()))
        if self.dcb.setting_straightness:
            a += int(tmp == self.dcb.threshset_straightness)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Finesse"].get()))
        if self.dcb.setting_power:
            a += int(tmp == self.dcb.threshset_power)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Finish"].get()))
        if self.dcb.setting_freeze:
            a += int(tmp == self.dcb.threshset_freeze)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Vibrate On Pass"].get()))
        if self.dcb.setting_vop:
            a += int(tmp == self.dcb.setting_vop)
        else:
            a += int(tmp == -1)

        tmp = int(val(self.options_configig["Disable All Vibrations"].get()))
        if self.dcb.setting_dvibe:
            a += int(tmp == self.dcb.setting_dvibe)
        else:
            a += int(tmp == -1)

        return a == 10

    def refresh_macaddrs(self):
        self.macaddrs.set('')
        self.macaddrs_combo['menu'].delete(0, 'end')
        self.macaddr_commands = []
        for choice in self.macaddrs_list:
            optioncmd = OptionList_Command_MacAddr(self)
            self.macaddr_commands.append(optioncmd)
            command = Tk._setit(optioncmd, choice)
            self.macaddrs_combo['menu'].add_command(
                label=choice, command=command)

    def timer(self):
        if self.dcb.macaddr not in self.macaddrs_list:
            if self.dcb.macaddr != None:
                # Only add DigiCue Blue devices / correct manuf. ID
                self.macaddrs_list.append(self.dcb.macaddr)
                if self.macaddr is None:
                    self.macaddr = self.dcb.macaddr
                    self.dcb.macaddr_filter = self.macaddr
                self.refresh_macaddrs()
                self.macaddrs.set(self.macaddr)

        if self.packet_count != self.dcb.packet_count:
            self.packet_count = self.dcb.packet_count

            # Update configuration
            self.refresh_setting_config()

            # Update graphics here
            if self.dcb.data_type == 0:  # Version packet
                pass
            elif self.dcb.data_type == 1:  # update gui if data packet
                self.scorebars.update()

        self.master.after(500, self.timer)
