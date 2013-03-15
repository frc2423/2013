
def configure_options(parser):
    
    parser.add_option('-i',
                      dest='static_images', default=None,
                      help='Specify an image file (or directory) to process')

    parser.add_option('--camera-ip', dest='camera_ip', default='10.24.23.11',
                      help='Specify the IP address of the camera')
    
    parser.add_option('--log-images', dest='log_images', default=False,
                      help='Log captured images to the log directory')
    
    #parser.add_option('--daisy', dest='daisy', default=False, action='store_true',
    #                  help='Run the Miss Daisy image processing code')
    
    #parser.add_option('--k2012', dest='kwarqs2012', default=False, action='store_true',
    #                  help='Run the Kwarqs 2012 image processing code')