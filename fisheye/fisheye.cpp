#include "fisheye.h"


#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <iostream>

using namespace std;
using namespace cv;

#define LOG(msg) std::cout << (msg) << std::endl

// FisheyeVideoConverter construction

FisheyeVideoConverter::FisheyeVideoConverter() { frame_check = 1; }

int FisheyeVideoConverter::calc_diameter(Mat frame) {
  Mat temp;
  cvtColor(frame(Rect(0, 0, frame.cols, frame.rows)), temp, CV_BGR2GRAY);
  equalizeHist(temp, temp);
  Scalar mean_value = mean(temp);
  threshold(temp, temp, mean_value[0] / 2, mean_value[0], 0);

  resize(temp, temp, Size(temp.cols, temp.rows));
  vector<vector<Point> > contours;
  vector<Vec4i> hierarchy;
  Mat temp_part(temp.rows / 2 + 10, temp.cols / 2 + 10, temp.type(),
                Scalar(255, 255, 255));
  temp(Rect(0, 0, temp.cols / 2, temp.rows / 2))
      .copyTo(temp_part(Rect(5, 5, temp.rows / 2, temp.rows / 2)));

  findContours(temp_part, contours, hierarchy, CV_RETR_TREE,
               CV_CHAIN_APPROX_SIMPLE, Point(0, 0));
  vector<vector<Point> > contours_poly(contours.size());
  vector<Rect> boundRect(contours.size());
  Rect dis_rect(0, 0, 0, 0);
  for (int i = 0; i < contours.size(); i++) {
    approxPolyDP(Mat(contours[i]), contours_poly[i], 3, true);
    boundRect[i] = boundingRect(Mat(contours_poly[i]));
    if (dis_rect.width < boundRect[i].width &&
        boundRect[i].width < temp_part.cols * 4 / 5)
      dis_rect = boundRect[i];
  }
  int dis;
  if (dis_rect.width < dis_rect.height)
    dis = dis_rect.width;
  else
    dis = dis_rect.height;
  dis = (int)sqrt(float((dis - frame.cols / 2) * (dis - frame.cols / 2) +
                        frame.rows / 2 * frame.rows / 2));
  return dis * 2;
}

void FisheyeVideoConverter::creat_map(int diameter, int degree) {
  diameter;
  float FOV =
      float(3.141592654 * degree / 180);  // FOV of the fisheye, eg: 180 degrees
  float f = diameter / (4 * sin(FOV / 2));
  map_x.create(Size(diameter, diameter), CV_32FC1);
  map_y.create(Size(diameter, diameter), CV_32FC1);

  for (int j = 0; j < diameter; j++) {
    for (int i = 0; i < diameter; i++) {
      // Polar angles
      float theta =
          float(2.0 * 3.14159265 * (i / (float)diameter - 0.5));  // -pi to pi
      float phi =
          float(3.14159265 * (j / (float)diameter - 0.5));  // -pi/2 to pi/2

      // Vector in 3D space
      float x = cos(phi) * sin(theta);
      float y = cos(phi) * cos(theta);
      float z = sin(phi);

      // Calculate fisheye angle and radius
      theta = atan2(z, x);
      phi = atan2(sqrt(x * x + z * z), y);
      float r = diameter * phi / FOV;

      // Pixel in fisheye space
      map_x.at<float>(j, i) = float(0.5 * diameter + r * cos(theta));
      map_y.at<float>(j, i) = float(0.5 * diameter + r * sin(theta));
    }
  }
}

int FisheyeVideoConverter::fisheye_convert(const std::string& input_file_path,
                                           const std::string& output_file_path,
                                           int degree, double rotation) {
  VideoCapture incap(input_file_path);
  if (!incap.isOpened()) {
    return -1;
  }
  // Setup output video
  VideoWriter output_cap;

  int diameter_temp[100], count_temp[100] = {0};
  for (int i = 0; i < 100; i++) {
    incap >> frame;
    if (!frame.empty())
      diameter_temp[i] =
          calc_diameter(frame(Rect(0, 0, frame.cols / 2, frame.rows)));
  }
  for (int i = 0; i < 99; i++) {
    if (diameter_temp[i] != -1) {
      for (int j = i + 1; j < 100; j++) {
        if (diameter_temp[i] == diameter_temp[j]) {
          count_temp[i]++;
          diameter_temp[j] = -1;
        }
      }
    }
  }
  int diameter = diameter_temp[0], count = count_temp[0];
  for (int i = 1; i < 100; i++) {
    if (count < count_temp[i]) {
      diameter = diameter_temp[i];
      count = count_temp[i];
    }
  }
  int x_pos = 4;
  int y_pos = 7;
  int replace_image = 0;
  creat_map(diameter, degree);
  bool create_writer = 1;
  while (frame_check) {
    incap >> frame;
    if (frame.empty()) {
      frame_check = 0;
    } else {
      Mat rotateMat;
      resize(frame, frame, Size(frame.cols, frame.rows));
      Mat temp_left(diameter, diameter, frame.type()),
          temp_right(diameter, diameter, frame.type());
      frame(Rect(0, 0, frame.cols / 2, frame.rows)).copyTo(temp_left(
          Rect((diameter - frame.cols / 2) / 2, (diameter - frame.rows) / 2,
               frame.cols / 2, frame.rows)));
      // frame(Rect(0, 0, frame.cols/2,
      // frame.rows)).copyTo(temp_left(Rect((diameter - frame.cols/2)/2,
      // (diameter - frame.rows)/2, frame.cols/2, frame.rows)));
      frame(Rect(frame.cols / 2, 0, frame.cols / 2, frame.rows))
          .copyTo(temp_right(Rect((diameter - frame.cols / 2) / 2,
                                  (diameter - frame.rows) / 2, frame.cols / 2,
                                  frame.rows)));
      //      rotateMat =
      // getRotationMatrix2D(Point(temp_left.cols/2, temp_left.rows/2) , r_rot *
      // rotation , 1 );
      //      warpAffine( temp_left, temp_left, rotateMat,
      // temp_left.size());
      //      rotateMat =
      // getRotationMatrix2D(Point(temp_right.cols/2, temp_right.rows/2) ,l_rot
      // *  rotation , 1 );
      //      warpAffine( temp_right, temp_right, rotateMat,
      // temp_right.size());

      remap(temp_left, temp_left, map_x, map_y, CV_INTER_LINEAR,
            BORDER_CONSTANT, Scalar(0, 0, 0));
      remap(temp_right, temp_right, map_x, map_y, CV_INTER_LINEAR,
            BORDER_CONSTANT, Scalar(0, 0, 0));

      temp_left = temp_left(
          Rect(temp_left.cols / 4 - temp_left.cols * (degree - 180) / 360, 0,
               temp_left.cols / 2 + temp_left.cols * (degree - 180) / 180,
               temp_left.rows));
      // line(temp_left, Point(temp_left.cols/4, 0), Point(temp_left.cols/4,
      // temp_left.rows), Scalar(0, 0, 0));
      temp_right = temp_right(
          Rect(temp_right.cols / 4 - temp_right.cols * (degree - 180) / 360, 0,
               temp_right.cols / 2 + temp_right.cols * (degree - 180) / 180,
               temp_right.rows));

      //      resize(temp_left, temp_left,
      // Size(temp_left.rows/3, temp_left.rows/3));
      //      resize(temp_right, temp_right,
      // Size(temp_right.rows/3, temp_right.rows/3));

      Mat show_frame(temp_left.rows, temp_left.cols * 2, temp_left.type());
      if (replace_image == 0) {
        rotateMat = getRotationMatrix2D(
            Point(temp_left.cols - temp_left.cols * (degree - 180) / 180,
                  temp_left.rows),
            -rotation, 1);
        warpAffine(temp_left, temp_left, rotateMat, temp_left.size());

        temp_left = temp_left(
            Rect(temp_left.cols * (degree - 180) / degree, 0,
                 temp_left.cols - temp_left.cols * (degree - 180) / degree,
                 temp_left.rows));
        temp_right = temp_right(Rect(
            temp_right.cols * (degree - 180) / degree, 0,
            temp_right.cols - temp_right.cols * (degree - 180) * 2 / degree,
            temp_right.rows));
        temp_left(Rect(0, 0, temp_left.cols, temp_left.rows - x_pos)).copyTo(
            show_frame(Rect(0, x_pos, temp_left.cols, temp_left.rows - x_pos)));
        temp_right(Rect(0, 0, temp_right.cols, temp_right.rows))
            .copyTo(show_frame(Rect(temp_right.cols - y_pos, 0, temp_right.cols,
                                    temp_right.rows)));
      } else {
        rotateMat = getRotationMatrix2D(
            Point(temp_right.cols - temp_right.cols * (degree - 180) / 180,
                  temp_right.rows),
            -rotation, 1);
        warpAffine(temp_right, temp_right, rotateMat, temp_left.size());

        temp_right = temp_right(
            Rect(temp_right.cols * (degree - 180) / degree, 0,
                 temp_right.cols - temp_right.cols * (degree - 180) / degree,
                 temp_right.rows));
        temp_left = temp_left(
            Rect(temp_left.cols * (degree - 180) / degree, 0,
                 temp_left.cols - temp_left.cols * (degree - 180) * 2 / degree,
                 temp_left.rows));
        temp_right(Rect(0, 0, temp_right.cols, temp_right.rows - x_pos))
            .copyTo(show_frame(
                Rect(0, x_pos, temp_right.cols, temp_right.rows - x_pos)));
        temp_left(Rect(0, 0, temp_left.cols, temp_left.rows)).copyTo(show_frame(
            Rect(temp_left.cols - y_pos, 0, temp_left.cols, temp_left.rows)));
      }

      show_frame = show_frame(Rect(
          20, 3, temp_left.cols + temp_right.cols - 120, show_frame.rows - 40));

      if (create_writer) {
        create_writer = 0;
        // namedWindow("show", 0);
        int ex = static_cast<int>(
            incap.get(CV_CAP_PROP_FOURCC));  // Get Codec Type- Int form

        output_cap.open(output_file_path, CV_FOURCC('D', 'I', 'V', 'X'),
                        incap.get(CV_CAP_PROP_FPS),
                        Size(show_frame.cols, show_frame.rows), true);
        if (!output_cap.isOpened()) {
          return -2;
        }
      }

      output_cap << show_frame;
      // double win_property = getWindowProperty("show", 2);
      // if (win_property == -1) {
      //   frame_check = 0;
      // }
      // imshow("show", show_frame);
      int c = waitKey(10);
      if (c == 'd') {
        replace_image = (replace_image + 1) % 2;
      }
    }
  }

  output_cap.release();
  //  output_cap.~VideoWriter();
  return 0;
}

// int main(int argc, char* argv[]) {
//   FisheyeVideoConverter fisheye_converter;
//   int ret = fisheye_converter.fisheye_convert(argv[1], argv[2], 190, 0.8);
//   std::cout << "returned " << ret << std::endl;
// }