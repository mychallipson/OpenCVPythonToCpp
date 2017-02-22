#
#  OpenCV Ball Tracking:
#

import cv2
import numpy as np
import os
import calendar
import time

####################################################################
#
#  Define defaults for each trackbar, for the YELLOW BALL ,
#  because the HUE ANGLES for red wrap around from -160 to 30 degrees
#  which makes this method for range clipping fail.
#
DEF_lH = 46 		# low  Hue 	-- lower  Hue Angle allowed.
DEF_uH = 127		# high Hue 	-- upper  Hue Angle allowed.
DEF_lS = 126		# low  Sat 	-- lower  saturation limit.
DEF_uS = 236		# high Sat 	-- upper  saturation limit.  Ignoring top 5 values ignores specular reflections.
DEF_lV = 56	    	# low  Value 	-- lower Value limit.
DEF_uV = 146		# high Value 	-- upper Value limit.


#
#  An empty function to call when a trackbar changes.
#  The trackbar generation function needs a function to call.
#
#  You could make one of these for each trackbar, and change some global variables.
#
def do_nada(x) :
    return x


###################################################################################################
def main():
    ESC_KEY 			= 27
    MAX_CIRCLES_TO_DRAW 	=  3
    SHOW_HSV_CHANNELS   	= False


    # Declare a VideoCapture object and associate to webcam, 0 => use first webcam
    capWebcam = cv2.VideoCapture(0)

    # Show original resolution
    print "default resolution = " + str(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) + \
				"x" + str(capWebcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Change the web camera's resolution to 320x240 for faster processing
    capWebcam.set(cv2.CAP_PROP_FRAME_WIDTH,  320.0)
    capWebcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240.0)

                                                      # show updated resolution
    print "updated resolution = " + str(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + \
		 str(capWebcam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if capWebcam.isOpened() == False:                           	# Check if VideoCapture object was
									# associated to webcam successfully
        print "error: capWebcam not accessed successfully\n\n"          # if not, print error message to std out
        os.system("pause")                                              # pause until user presses a key so
									# user can see error message
        return                                                          # and exit function (which exits program)
    # end if


    #  Create windows, use WINDOW_AUTOSIZE for a fixed window size
    #  Or, use WINDOW_NORMAL to allow window resizing
    cv2.namedWindow(   "imgOriginal", 	cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(   "CombinedFeats", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(   "Thresholds", 	cv2.WINDOW_NORMAL)

    if SHOW_HSV_CHANNELS : 
        cv2.namedWindow("imHue", 	cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("imSaturation",	cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("imValue", 	cv2.WINDOW_AUTOSIZE)
    #endif


    # Track bars
    # Copied from: http://stackoverflow.com/questions/33631460/...
    #                 ...why-doesnt-opencvs-inrange-function-convert-my-hsv-image-to-binary
    cv2.createTrackbar( "Low  Hue",   "Thresholds", 0, 180, do_nada )
    cv2.createTrackbar( "High Hue",   "Thresholds", 0, 180, do_nada )
    cv2.createTrackbar( "Low  Sat",   "Thresholds", 0, 255, do_nada )
    cv2.createTrackbar( "High Sat",   "Thresholds", 0, 255, do_nada )
    cv2.createTrackbar( "Low  Value", "Thresholds", 0, 255, do_nada )
    cv2.createTrackbar( "High Value", "Thresholds", 0, 255, do_nada )


    # MOVE AND RESIZE WINDOWS:
    cv2.moveWindow(    "imgOriginal",     0,  35 );
    cv2.moveWindow(    "CombinedFeats",   0, 600 );
    cv2.resizeWindow(  "Thresholds",    640, 380 );
    cv2.moveWindow(    "Thresholds",    640,  35 );


    # Set the defaults:
    cv2.setTrackbarPos( "Low  Hue",   "Thresholds", DEF_lH );
    cv2.setTrackbarPos( "High Hue",   "Thresholds", DEF_uH );
    cv2.setTrackbarPos( "Low  Sat",   "Thresholds", DEF_lS );
    cv2.setTrackbarPos( "High Sat",   "Thresholds", DEF_uS );
    cv2.setTrackbarPos( "Low  Value", "Thresholds", DEF_lV );
    cv2.setTrackbarPos( "High Value", "Thresholds", DEF_uV );

    frameCount = 0
    startTime = calendar.timegm(time.gmtime())

    # Repeat until the Esc key is pressed or the webcam connection is lost:
    while cv2.waitKey(1) != ESC_KEY and capWebcam.isOpened():

        frameCount = frameCount + 1

        blnFrameReadSuccessfully, imgOriginal = capWebcam.read()            # read next frame
        # Check for errors :
        if not blnFrameReadSuccessfully or imgOriginal is None:             # if frame was not read successfully
            print "error: frame not read from webcam\n"                     # print error message to std out
            os.system("pause")                                              # pause until user presses a key
									    # so user can see error message
            break                                                           # exit while loop (which exits program)
        # end if

	#############################################################
	#
        #  NORMAL PROCESSING IS HERE:
	#

	# Convert BGR image to HSV:
        imgHSV		= cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

	# Getting values from track bars:
	lH = cv2.getTrackbarPos("Low  Hue", "Thresholds")		# low  Hue
	uH = cv2.getTrackbarPos("High Hue", "Thresholds")		# high Hue
	lS = cv2.getTrackbarPos("Low  Sat", "Thresholds")		# low  Sat
	uS = cv2.getTrackbarPos("High Sat", "Thresholds")		# high Sat
	lV = cv2.getTrackbarPos("Low  Value", "Thresholds")		# low  Value
	uV = cv2.getTrackbarPos("High Value", "Thresholds")		# high Value

	tbk_method = False
        if tbk_method :
	    bImLowHue		= cv2.inRange(imgHSV[:,:,0],   0,  40 )
	    bImHighSat		= cv2.inRange(imgHSV[:,:,1], 110, 255 )
	    bImMidValue		= cv2.inRange(imgHSV[:,:,2], 128, 255 )
	    # bImThreshLow	= cv2.inRange(imgHSV, np.array([0, 135, 135]), np.array([18, 255, 255]))
	    # bImThreshHigh	= cv2.inRange(imgHSV, np.array([165, 135, 135]), np.array([179, 255, 255]))

	    imgThresh	= cv2.multiply( cv2.multiply( bImLowHue, bImMidValue ), bImHighSat );
        else :
	    # Method from other web page
	    lowerb 	= np.array([lH, lS, lV], np.uint8)
	    upperb 	= np.array([uH, uS, uV], np.uint8)
	    imgThresh 	= cv2.inRange( imgHSV, lowerb, upperb )

    	#  Do some morphological processing to remove some noise.
	#  This is a "Close"-ish operation, because it dilates then erodes, but TBK dilates more than erodes
        imgThresh	= cv2.dilate(imgThresh, np.ones((7,7),np.uint8))
        imgThresh	= cv2.erode(imgThresh, np.ones((7,7),np.uint8))

    	# Blur the results to convert the image from a binary image to
	# a gradient image, so that the Canny Edge detectors will work.
        imgThresh	= cv2.GaussianBlur(imgThresh, (3, 3), 2, 2)

	#  The "shape" of an image is the size of data matrix that holds the image:
        nRows, nCols 	= imgThresh.shape

   	#  Use a Hough Circle detector.
 	#  Fill variable circles with all circles in the processed image
	#
        #  cv.HOUGH_GRADIENT is the edge Method used.  This is the only one possible.
	#  See parameter descriptions at end of file.

	hough_sub_sampling 	= 4  			# 2 worked, but higher values run faster.
        min_dist 	 	= nRows / 5
        canny_max 		= 200			# Expect very high contrast edges.
        canny_min               =  56			# Again, expect that high contrast will be sufficient.
        min_radius              =  18			# Resolution dependent
        max_radius              =  85			# Resolution dependent
        circles 	= cv2.HoughCircles(imgThresh, cv2.HOUGH_GRADIENT, hough_sub_sampling, min_dist, \
	 			canny_max , canny_min ) # ,
	 			# ) # min_radius, max_radius )
        # circles 	= cv2.HoughCircles(imgThresh, cv2.HOUGH_GRADIENT, hough_sub_sampling, min_dist )
				# canny_max, canny_min, \
				# min_radius, max_radius )


        # Prevent the program from crashing on next line if no circles were found.
        if circles is not None:
	    # print "--------------"
	    # Python returns a vector of vectors, even though there is only one element there.
	    set_of_circles = circles[0];
            n_circles, n_params_per_circle = set_of_circles.shape
	    max_circles = n_circles
	    if max_circles > MAX_CIRCLES_TO_DRAW :
		max_circles = MAX_CIRCLES_TO_DRAW ;

            for idx in range(0,max_circles) :
		circle = set_of_circles[idx,:]
                x, y, radius = circle                           # Break out x, y, and radius

		if radius <= max_radius :
                    timeDiff = calendar.timegm(time.gmtime()) - startTime
                    fps = int(frameCount / timeDiff)
                    print "ball     position x = " + str(x) + ", y = " + str(y) + ", radius = " + \
		    	str(radius) + ", fps = " + str(fps) # print ball position and radius
  		    # draw small green circle at center of detected object
                    cv2.circle(imgOriginal, (x, y), 4, (0, 255, 128), -1)
		    # draw large circle around the detected object
                    cv2.circle(imgOriginal, (x, y), radius, (255,  0, 255), 5)
                    cv2.circle(imgThresh,   (x, y), radius, (255,255,  64), 3)
		# else :
                    # print "ignoring position x = " + str(x) + ", y = " + str(y) + ", radius = " + \
		    #		str(radius) # print ball position and radius
		    # draw large circle around the ignored object:
                    # cv2.circle(imgOriginal, (x, y), radius, (0, 192, 255), 3)
		# end if
            # end for
        # end if

        # Show image, findings, and features:
        cv2.imshow("imgOriginal", imgOriginal)
        # cv2.imshow("imHue", 	     imgHSV[:,:,0] )
        # cv2.imshow("imSaturation", imgHSV[:,:,1] )
        # cv2.imshow("imValue",      imgHSV[:,:,2] )

        if tbk_method :
            cv2.imshow("imHue",  	bImLowHue );
            cv2.imshow("imSaturation",  bImHighSat );
            cv2.imshow("imValue",       bImMidValue );

        cv2.imshow("CombinedFeats",   imgThresh );

        # cv2.imshow("imHue", 	      imgHSV[:,:,0] );
        # cv2.imshow("imSaturation",  imgHSV[:,:,1] );
        # cv2.imshow("imValue",       imgHSV[:,:,2] );
        # cv2.imshow("CombinedFeats", imgThresh );
    # end while

    cv2.imwrite( "Results.jpg",    imgOriginal )
    cv2.imwrite( "Features.jpg",   imgThresh   )

    cv2.destroyAllWindows()                     # remove windows from memory

    return

###################################################################################################
if __name__ == "__main__":
    main()


#  cv.HOUGH_GRADIENT is the edge Method used.  This is the only one possible.
#  hough_resolution = 2 is the how much to sub sample HoughSpace by
#
# circles - Output vector of found circles.
#  Each vector is encoded as a 3-element floating-point vector (x, y, radius) .
#
#  Use a Hough Circle detector.
#  Fill variable circles with all circles in the processed image
#
# image = 8-bit, single-channel, grayscale input image.
#     cv.HOUGH_GRADIENT is the edge Method used.  This is the only one possible.
# circle_storage = In C function this is a memory storage that will
#     contain the output sequence of found circles.
# method = Detection method to use. Currently, the only implemented
#     method is CV_HOUGH_GRADIENT , which is basically 21HT , described in [Yuen90].
# dp = Inverse ratio of the accumulator resolution to the image
#     resolution. For example, if dp=1 , the accumulator has the same resolution
#     as the input image. If dp=2 , the accumulator has half as big width
#     and height.
# minDist - Minimum distance between the centers of the detected
#     circles. If the parameter is too small, multiple neighbor circles may
#     be falsely detected in addition to a true one. If it is too large,
#     some circles may be missed.
# param1 - First method-specific parameter. In case of CV_HOUGH_GRADIENT,
#     it is the higher threshold of the two passed to the Canny() edge
#     detector (the lower one is twice smaller).
# param2 - Second method-specific parameter. In case of
#     CV_HOUGH_GRADIENT , it is the accumulator threshold for the circle centers
#     at the detection stage. The smaller it is, the more false circles may
#     be detected. Circles, corresponding to the larger accumulator values,
#     will be returned first.
# minRadius - Minimum circle radius.
# maxRadius - Maximum circle radius.
