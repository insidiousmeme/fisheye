#ifndef FISHEYE_H_
#define FISHEYE_H_

#include <opencv2/imgproc.hpp>
#include <string>

class FisheyeVideoConverter {
 public:
  FisheyeVideoConverter();
  int Convert(const std::string& input_file_path,
              const std::string& output_file_path, double degree,
              double rotation, const std::string& watermark_text = "");

 private:
  void AddWatermarkTextToFrame(const std::string& text, cv::Mat& frame);
  int CalcDiameter(cv::Mat frame);
  void CreateMap(int diameter, int degree);

  cv::Mat map_x;
  cv::Mat map_y;
  cv::Mat frame;
  bool frame_check;
};

#endif  // FISHEYE_H_ls
