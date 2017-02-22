#include<opencv2\imgproc\imgproc.hpp>
#include<opencv2\highgui\highgui.hpp>
#include<iostream>

int DEF_lH = 15;
int DEF_uH = 35;
int DEF_lS = 120;
int DEF_uS = 250;
int DEF_lV = 150;
int DEF_uV = 255;

using namespace std;

int main(int argc, char* argv[]) {
	int ESC_KEY = 27;
	int MAX_CIRCLES_TO_DRAW = 3;
	bool SHOW_HSV_CHANNELS = false;

	cv::VideoCapture capWebcam = cv::VideoCapture(0);

	cout << "default resolution" << capWebcam.get(cv::CAP_PROP_FRAME_WIDTH) << "x"
		<< capWebcam.get(cv::CAP_PROP_FRAME_HEIGHT) << endl;

	capWebcam.set(cv::CAP_PROP_FRAME_WIDTH, 320.0);
	capWebcam.set(cv::CAP_PROP_FRAME_HEIGHT, 240.0);

	cout << "updated resolution" << capWebcam.get(cv::CAP_PROP_FRAME_WIDTH) << "x"
		<< capWebcam.get(cv::CAP_PROP_FRAME_HEIGHT) << endl;

	if (!capWebcam.isOpened()) {
		cerr << "error: capWebcam not access successfully" << endl;
		cin.ignore();
		return;
	}

	cv::namedWindow("imgOriginal", cv::WINDOW_AUTOSIZE);
	cv::namedWindow("CombinedFeats", cv::WINDOW_AUTOSIZE);
	cv::namedWindow("Thresholds", cv::WINDOW_NORMAL);

	if (SHOW_HSV_CHANNELS) {
		cv::namedWindow("imHue", cv::WINDOW_AUTOSIZE);
		cv::namedWindow("imSaturation", cv::WINDOW_AUTOSIZE);
		cv::namedWindow("imValue", cv::WINDOW_AUTOSIZE);
	}
	cv::createTrackbar("Low Hue", "Thresholds", 0, 180, cv::TrackbarCallback());
	cv::createTrackbar("High Hue", "Thresholds", 0, 180, cv::TrackbarCallback());
	cv::createTrackbar("Low Sat", "Thresholds", 0, 255, cv::TrackbarCallback());
	cv::createTrackbar("High Sat", "Thresholds", 0, 255, cv::TrackbarCallback());
	cv::createTrackbar("Low Value", "Thresholds", 0, 255, cv::TrackbarCallback());
	cv::createTrackbar("High Value", "Thresholds", 0, 255, cv::TrackbarCallback());

	cv::moveWindow("imgOriginal", 0, 35);
	cv::moveWindow("CombinedFeats", 0, 600);
	cv::resizeWindow("Thresholds", 640, 380);
	cv::moveWindow("Thresholds", 640, 35);

	cv::setTrackbarPos("Low Hue", "Thresholds", DEF_lH);
	cv::setTrackbarPos("High Hue", "Thresholds", DEF_uH);
	cv::setTrackbarPos("Low Sat", "Thresholds", DEF_lS);
	cv::setTrackbarPos("High Sat", "Thresholds", DEF_uS);
	cv::setTrackbarPos("Low Value", "Thresholds", DEF_lV);
	cv::setTrackbarPos("High Value", "Thresholds", DEF_uV);

	cv::Mat imgOriginal;
	cv::Mat imgHSV, imgHSVB, imgHSVG, imgHSVR;
	cv::Mat bImLowHue;
	cv::Mat bImHighSat;
	cv::Mat bImMidValue;
	cv::Mat imgThresh;
	cv::Mat lowerb, upperb;
	while (cv::waitKey(1) != ESC_KEY && capWebcam.isOpened()) {
		if (!capWebcam.read(imgOriginal)) {
			cerr << "error: frame not read from webcam" << endl;
			cin.ignore();
			break;
		}
		cv::cvtColor(imgOriginal,imgHSV, cv::COLOR_BGR2HSV);
		int lH = cv::getTrackbarPos("Low Hue", "Thresholds");
		int uH = cv::getTrackbarPos("High Hue", "Thresholds");
		int lS = cv::getTrackbarPos("Low Sat", "Thresholds");
		int uS = cv::getTrackbarPos("High Sat", "Thresholds");
		int lV = cv::getTrackbarPos("Low Value", "Thresholds");
		int uV = cv::getTrackbarPos("High Value", "Thresholds");

		bool tbk_method = false;
		if (tbk_method) {
			cv::extractChannel(imgHSV, imgHSVB, 0);
			cv::extractChannel(imgHSV, imgHSVG, 1);
			cv::extractChannel(imgHSV, imgHSVR, 2);
			cv::inRange(imgHSVB, 0, 40, bImLowHue);
			cv::inRange(imgHSVG, 110, 255, bImHighSat);
			cv::inRange(imgHSVR, 128, 255, bImMidValue);
			
			cv::Mat intermediate;
			
			cv::multiply(bImLowHue, bImMidValue, intermediate);
			cv::multiply(intermediate, bImHighSat, imgThresh);


		}
		else {
			int lSizes[] = { lH,lS,lV };
			int uSizes[] = { uH,uS,uV };
			lowerb = cv::Mat(3, lSizes, CV_8UC3);
			upperb = cv::Mat(3, uSizes, CV_8UC3);
			cv::inRange(imgHSV, lowerb, upperb, imgThresh);
		}

		cv::dilate(imgThresh, imgThresh, cv::Mat::ones(7, 7, CV_8UC1));
		cv::erode(imgThresh, imgThresh, cv::Mat::ones(7, 7, CV_8UC1));

		cv::GaussianBlur(imgThresh, imgThresh, cv::Size(3, 3), 2, 2);

		cv::Size shape = imgThresh.size();

		int hough_sub_sampling = 4;
		int min_dist = shape.height / 5;
		int canny_max = 200;
		int canny_min = 56;
		int min_radius = 18;
		int max_radius = 85;
		vector<cv::Vec3f> circles;
		cv::HoughCircles(imgThresh,circles, cv::HOUGH_GRADIENT, hough_sub_sampling, min_dist, canny_max, canny_min);

		if (!circles.empty) {
			cv::Vec3f set_of_circles = circles[0];
			//Stuck at line 183 in the python code
		}

		//Picked up at line 211
		cv::imshow("imgOriginal", imgOriginal);

		if (tbk_method) {
			cv::imshow("imHue", bImLowHue);
			cv::imshow("imSaturation", bImHighSat);
			cv::imshow("imValue", bImMidValue);
		}
		cv::imshow("CombinedFeats", imgThresh);
	}

	cv::imwrite("Results.jpg", imgOriginal);
	cv::imwrite("Features.jpg", imgThresh);

	cv::destroyAllWindows();

	return 0;
}