</b>OVERVIEW/>

This project contains a Graphical User Interface for Desktops that interfaces with the DigiCue Blue (made by OB Cues) and the BLED112 Bluetooth USB dongle (made by Silicon Labs, sold separately from the DigiCue Blue). The project is written in Python for portability, and includes a py2exe script for compiling to a Windows executable. No system installation is necessary and the program can run from the directory. Run main.py or main.exe to start. serialport.py is the serial port selection GUI, and will load automatically if comport.cfg is blank or does not exist. The program appends comma-delimited data into data.csv for each shot.

You are free to modify and redistribute this code as long as you include the MIT license with your distribution.
For any questions, please contact Nathan Rhoades at nataddrho(at)gmail(dot)com.

---

BLED112 USB DONGLE

The BLED112 USB dongle is a small Bluetooth low energy transceiver with built-in antenna available from Silicon Labs. See https://www.silabs.com/products/wireless/bluetooth/bluetooth-low-energy-modules/bled112-bluetooth-smart-dongle. It is also available for purchase through a variety of distributors. This software will work with any serial device that interprets Bluegiga commands. Other third-party Bluetooth dongles are not supported.

---

DIGICUE BLUE

The DigiCue Blue is a small electronic coach that attaches to the end of your pool, snooker, or billiards cue. The device communicates with your mobile device via Bluetooth and helps improve your game. See www.digicue.net for more information. Please note that the original DigiCue does not support wireless communication.

---

HOW TO USE
1. Insert the DigiCue Blue into the rubber housing that best fits your cue (there are two sizes) with the power switch notch aligned with the center of the DigiCue Logo. (See image A).

2. Push the DigiCue Blue down towards the bottom of the rubber housing so that the Power Button Circle is in line with the power button on the DigiCue Blue. (See image B). A rib in the inside of the housing will hold the DigiCue Blue in place.

3. Slide the rubber housing onto the butt end of your cue, so that end of your cue makes physical contact with the DigiCue Blue plastic cap.

4. Purchase a BLED112 Bluetooth USB dongle from Silicon Labs and insert it into your USB port of your computer. Alternatively, download the DigiCue app to your mobile device. Both iOS and Android apps are available.

5. Open the Configure tab and press the power button on the DigiCue Blue once. The MAC address of the DigiCue Blue should appear. If there are multiple DigiCue Blues available, select which one you want to connect to.

6. Play your favorite billiards game. The DigiCue Blue will vibrate when a fault is detected in your stroke, and will wirelessly send information to your computer or mobile device. Each metric is customizable and gives you full control over many aspects of your stroke fundamentals. To customize the DigiCue Blue settings, go to the Configure tab and select the options you want. Then press the DigiCue Blue power button twice and hold it close to the USB dongle or mobile device. The DigiCue Blue will vibrate four times when successfully configured.

7. To remove the DigiCue Blue from the rubber housing, push with your thumb on the spot on the rubber housing as indicated in image C until the unit dislodges. Do NOT push up from the very bottom of the rubber housing as this could damage the DigiCue Blue.

8. You must complete a product registration form within 30 days of purchase to activate the warranty. The DigiCue Blue warranty form is available online at www.obcues.com.

Battery Replacement: Common non-rechargeable CR2032 lithium ion battery.

---

FAULT DESCRIPTIONS

Everytime the USB dongle receives a shot from the selected DigiCue Blue, it will update a horizontal bar graph displaying metrics of eight different parameters of your stroke. The bar graph will fill from the left to the right, with the highest score as a completely filled bar. Each bar has a vertical black line indicating the currently selected threshold level. These can be changed in the Config tab. Values less than the threshold will be displayed as red, and values equal to or more than the threshold will be displayed as green. The actual value of each shot score is displayed numerically. Also, a smaller gray bar under each bar shows the average score for the current instance that the program is opened. Close and re-open the program to reset.

All data is logged in data.csv in comma-delimited format. You may copy, rename, save, maintain, and plot these data files as you wish. 


JAB

Measures the amount of rapid deceleration of the cue after impact with a score from 1 to 10. A low score of 1 means that the cue was pulled back towards the player very quickly after impact with the cue ball, and a high score of 10 means that the cue was not pulled back towards the player at all.

Achieve a high score to reduce pre-impact-anticipation from causing tip location errors and increase the predictability in accuracy and power. 


FOLLOW THROUGH

Measures the smoothness and acceleration of the cue during and after impact with a score from 1 to 10. A low score of 1 means that the follow through was extremely abrupt and punchy with a fast deceleration. A high score of 10 means that the cue smoothly accelerated through the cue ball with a graceful pushing motion.

A high score generally correlates to a higher consistency in cue ball speed control and accuracy because there is zero deceleration of the cue during impact. Any deceleration may pull back on the cue and cause the tip to slightly veer off of the anticipated path leading to a greater spread in aiming errors.

High scores can still be achieved with good acceleration and a physically short follow through length.


FINISH

Measures the length of time that the cue remains reasonably motionless 0.5 seconds after impact, up to 3.5 seconds. A score of 0.5 seconds means that the player did not keep the cue still for at least 0.5 seconds after impact, where as a score of 3.5 seconds means that the player kept the cue still for at least 3.5 seconds. A small amount of movement is tolerable to allow the motion of the cue and arm to come to rest, but any more caused by unnecessary body motion or not staying down on the table will cause a fault.

Achieve a high score to improve consistency in fundamentals and stance by eliminating body movement, head movement, loose foundation, and lack of focus and commitment. Improves the habit of watching exactly where the cue ball contacts the object ball, leading to a higher level of awareness of cue ball control and accuracy.


TIP STEER

Measures the amount of left or right force applied to the cue immediately before impact with a score from 1 to 10. A low score of 1 means that a significant amount of sideways force was applied during the forward stroke to cause the tip to steer either to the left or right. A high score of 10 means that almost zero sideways force was applied during the forward stroke and that the motion of the cue remained along to the vertical axis. Higher threshold settings require the cue to remain closer to the vertical axis. Pendulum strokes and shoulder drop strokes will not result in low scores if the motion remains along the vertical axis.

Achieve a high score to improve tip accuracy and stroke mechanics, and to eliminate the use of body English, steering, swooping, and unintentionally moving the cue off of the vertical stroke plane.


STRAIGHTNESS

Measures the amount of radial force (in any direction) applied to the cue immediately before impact with a score from 1 to 10. A low score of 1 means that a significant amount of radial force was applied during the forward stroke to cause the tip to move in a direction other than a straight line. A high score of 10 means that almost zero radial force was applied during the forward stroke and that the motion of the cue stayed along a straight line. Pendulum strokes and shoulder drop strokes may result in low scores even if the cue remains along the vertical axis, whereas perfect piston strokes will not.

Achieve a high score to improve tip accuracy and stroke mechanics, and to eliminate the use of body English, steering, swooping, and unintentionally moving the cue off of the stroke line.

Straightness is also plotted, viewed from behind the cue looking towards the cue ball. The plot represents the direction of the movement of the tip off of the shotline immediately before impact with the cue ball.


FINESSE

Measures the amount of speed or power transferred to the cue ball with a score from 1 to 10. A score of 1 means that the cue ball was hit at a medium speed, while a score of 10 means that the cue ball was hit at a very soft speed.

Achieve a high score to practice soft shots and finesse. Attempt to achieve both a high score in finesse and follow through simultaneously.


SHOT INTERVAL

Measures the amount of time between shots up to 2 minutes. A fault will occur if the time between shots is less than the selected threshold.

Useful in helping players with pace and preventing rushed shots.


BACKSTROKE PAUSE

Measures the amount of time that the cue remains reasonably motionless before the final forward stroke, up to 1.5 seconds.

Achieve a long pause time to eliminate backstroke to forward stroke transition errors and maintain tip placement consistency and cue alignment.

---
OB Cues 962 N Ave, Suite 700, Plano, TX 75074
