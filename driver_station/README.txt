 
KwarqsDashboard
---------------

    KwarqsDashboard is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

    KwarqsDashboard is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KwarqsDashboard.  If not, see <http://www.gnu.org/licenses/>.
    

KwarqsDashboard is an award-winning control system developed in 2013 for 
FIRST Robotics Team 2423, The Kwarqs. For the second year in a row, Team
2423 won the Innovation in Control award at the 2013 Boston Regional. 
The judges cited this control system as the primary reason for the award. 

It is designed to be used with a touchscreen, and robot operators use it
to select targets and fire frisbees at the targets.

Features
--------

- Written entirely in Python
	- Cross platform, fully functional in Linux and Windows 7/8

- All control/feedback features use NetworkTables, so the same robot can
be controlled using the SmartDashboard instead if needed
	- SendableChooser compatible implementation for mode switching

- Animated robot drawing that shows how many frisbees are present, and 
tilts the shooter platform according to the current angle the platform
is actually at.

- Allows operators to select different modes of operation for the robot,
using brightly lit toggle switches
	
- Operators can choose an autonomous mode on the dashboard, and set which
target the robot should aim for in modes that use tracking

- Switches operator perspective when robot switches modes

- Simulated lighted rocker switches to activate robot systems

- Logfiles written to disk with errors when they occur

Target acquisition image processing using a camera:

	- Tracks the selected targets in a live camera stream, and determines
	adjustments the robot should make to aim at the target
	- User can click on targets to tell the robot what to aim at
	- Differentiates between top/middle/low targets
	- Partially obscured targets can be identified
	- Target changes colors when the robot is aimed properly

Fully integrated realtime analysis support for target acquisition:
 
	- Adjustable thresholding, saves settings to file
	- Enable/disable drawing features and labels on detected targets
	- Show extra threshold images
	- Can log captured images to file, once per second

	- Can load a directory of images for analysis, instead of connecting to
	a live camera

Installation/Prerequisites
--------------------------

KwarqsDashboard has been developed/tested on the following platforms:

- Windows 7 x64 (32-bit python)
- Windows 8 x64 (32-bit python)
- Ubuntu 12.10 x64 (64-bit python)

You must have the following things installed to run the dashboard:

- Python 2.7
- pynetworktables 2013.4 or above
- PyGTK 2.24 and dependencies
	- GTK+, GObject, GLib, etc
- OpenCV 2.x (tested on 2.4.4) python bindings, with FFMPEG wrappers for OpenCV
- NumPy (tested on 1.6 and 1.7)

Windows specific install notes
------------------------------

To connect to the camera, you must have the FFMPEG wrappers for OpenCV
installed. On Windows, the wrapper is called opencv_ffmpeg244.dll, and
must be installed in C:\Python27 . If it is not installed correctly,
OpenCV will fail silently when trying to connect to the camera.

You can install PyGTK from pygtk.org, but it is old and buggy. I have
preferred to install the GStreamer SDK, and use their PyGTK bindings
instead. To actually run the code successfully, you need to set the
following environment variables up:

	set PATH=%PATH%;c:\gstreamer-sdk\0.10\x86\bin
	set PYTHONPATH=%PATH;c:\gstreamer-sdk\0.10\x86\lib\python2.7\site-packages

See launcher.au3 for an example of how to setup the environment correctly.

If you want to use launcher.au3 to launch the dashboard, then you
should install AutoIt and compile the script to an exe.

Code Credits
------------

Some code structuring ideas and PyGTK widget ideas were derived from my work
with Exaile (http://www.exaile.org/).

Team 341 graciously open sourced their image processing code in 2012, and
the image processing is heavily derived from a port of that code to python. 

	http://www.chiefdelphi.com/media/papers/2676
	
Sam Rosenblum helped develop the idea for the dashboard, and helped refine 
some of the operating concepts.

Stephen Rawls helped refine the image processing code and distance 
calculations.

Youssef Barhomi created image processing stuff for the Kwarqs in 2012, and
some of the ideas from that code were copied.


Image Credits
-------------
 
The included images were obtained from various places:

    - Linda Donoghue created the robot images
    - Buttons were obtained via google image search, I don't recall where
    - The fantastic lighted rocker switches were created by Keith Sereby,
    and can be found at http://dribbble.com/shots/409882-Lighted-Rocker-Switch 
    The derived rocker switch images are distributed with permission.

Support
-------

If you run into problems trying to get this to work, I highly recommend using
google to figure out how to solve your problem. The ChiefDelphi forums are an
excellent source of help also. 

Dustin Spicuzza, Team 2423
dustin@virtualroadside.com

