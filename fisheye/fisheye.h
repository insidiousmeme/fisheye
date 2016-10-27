#ifndef FISHEYE_H_
#define FISHEYE_H_

#include <opencv2/imgproc.hpp>

#include <string>

class FisheyeVideoConverter {
 public:
  FisheyeVideoConverter();
  int fisheye_convert(const std::string& input_file_path,
                      const std::string& output_file_path, int degree,
                      double rotation);

 private:
  int calc_diameter(cv::Mat frame);
  void creat_map(int diameter, int degree);

  cv::Mat map_x;
  cv::Mat map_y;
  cv::Mat frame;
  bool frame_check;
};

#endif  // FISHEYE_H_ls
