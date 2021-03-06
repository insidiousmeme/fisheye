#ifndef FISHEYE_H_
#define FISHEYE_H_

#include <opencv2/imgproc.hpp>
#include <string>

enum Codec {
  CODEC_MPEG_4,
  CODEC_MPEG_1,
  CODEC_FLV1,
/*
  // TODO: unworking codecs yet
  CODEC_MOTION_JPEG,
  CODEC_MPEG_4_2,
  CODEC_MPEG_4_3,
  CODEC_H263,
  CODEC_H263I
*/
};

class FisheyeVideoConverter {
 public:
  FisheyeVideoConverter();
  int Convert(const std::string& input_file_path,
              const std::string& output_file_path, double degree,
              double rotation, const std::string& watermark_text = "",
              Codec codec = CODEC_MPEG_4);

 private:
  void AddWatermarkTextToFrame(const std::string& text, cv::Mat& frame);
  int CalcDiameter(cv::Mat frame);
  void CreateMap(int diameter, int degree);

  cv::Mat map_x;
  cv::Mat map_y;
  cv::Mat frame;
  bool frame_check;
};

#endif  // FISHEYE_H_