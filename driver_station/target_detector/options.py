#
#   This file is part of KwarqsDashboard.
#
#   KwarqsDashboard is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3.
#
#   KwarqsDashboard is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with KwarqsDashboard.  If not, see <http://www.gnu.org/licenses/>.
#

def configure_options(parser):
    
    parser.add_option('-i',
                      dest='static_images', default=None,
                      help='Specify an image file (or directory) to process')
    
    parser.add_option('--ask',
                      dest='ask', default=False, action='store_true',
                      help='The program will ask the user for a logdir directory')
    
    parser.add_option('--webcam', dest='webcam', default=None, type='int',
                      help='Use a local webcam instead of a network camera')

    parser.add_option('--camera-ip', dest='camera_ip', default='10.24.23.11',
                      help='Specify the IP address of the camera')
    
    parser.add_option('--log-images', dest='log_images', default=False, action='store_true',
                      help='Log captured images to the log directory')
    
    #parser.add_option('--daisy', dest='daisy', default=False, action='store_true',
    #                  help='Run the Miss Daisy image processing code')
    
    #parser.add_option('--k2012', dest='kwarqs2012', default=False, action='store_true',
    #                  help='Run the Kwarqs 2012 image processing code')