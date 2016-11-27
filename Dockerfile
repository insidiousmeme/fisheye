FROM fedora:24
MAINTAINER Dmitry Belous (dmigous@gmail.com)

# Install RPM Fusion repository to install ffmpeg and related packages
RUN dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install dependencies
RUN dnf install -y \
  cmake \
  ffmpeg \
  ffmpeg-devel \
  findutils \
  gcc-c++ \
  gstreamer \
  gstreamer-devel \
  gstreamer-ffmpeg \
  gstreamer-plugins-base-devel \
  gstreamer1-libav \
  gtk2-devel \
  httpd \
  make \
  procps-ng \
  python3-devel \
  python3-mod_wsgi \
  redhat-rpm-config \
  swig \
  unzip \
  wget

# Download and build/install opencv and remove downloaded archive and build folder
# to reduce image size
RUN cd ~ && \
  wget -q https://github.com/opencv/opencv/archive/3.1.0.zip && \
  unzip 3.1.0.zip && \
  cd opencv-3.1.0/ && \
  mkdir build && \
  cd build && \
  CFLAGS=-fPIC CXXFLAGS=-fPIC cmake .. -DWITH_FFMPEG=ON -DCMAKE_CXX_COMPILER_ID=/usr/bin/clang++ -DCMAKE_C_COMPILER_ID=/usr/bin/clang -DCMAKE_INSTALL_PREFIX=/usr && \
  make -j4 && \
  make install && \
  cd ~ && \
  rm -rf ./opencv*

# Remove libippicv dependency from opencv.pc. Since it isn't used and breaks build
RUN sed -ir 's/\-lippicv//' /usr/lib/pkgconfig/opencv.pc

# Set env variables
ENV LD_LIBRARY_PATH /usr/lib/:/usr/lib64/
ENV PKG_CONFIG_PATH /usr/lib/pkgconfig

# Set default Python 3
RUN alternatives --install /usr/bin/python python /usr/bin/python3.5 2 && \
  alternatives --install /usr/bin/python python /usr/bin/python2.7 1 && \
  alternatives --set python /usr/bin/python3.5

# Add script to run apache web server from inside docker container
ADD ./fisheye_webservice/util/run_apache_foreground /etc/httpd/