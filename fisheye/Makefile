ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

OPENCV_CFLAGS:=`pkg-config --cflags opencv`
OPENCV_LIBS:= `pkg-config --libs opencv`



all: libfisheye.so

libfisheye.so: fisheye.cpp fisheye.h
	$(CXX) $< ${OPENCV_CFLAGS} ${OPENCV_LIBS} -o $@ -shared -fPIC

main: libfisheye.so main.cpp
	$(CXX) main.cpp -o $@ ${OPENCV_CFLAGS} -L. -lfisheye -lopencv_videoio ${OPENCV_LIBS}

fisheye_py: swig/fisheye.i libfisheye.so
	python --version
	swig -version
	cd python && swig -c++ -python -py3 -outcurrentdir -I${ROOT_DIR} ${ROOT_DIR}/$<
	cd python && python ./setup.py build

fisheye_py_install: fisheye_py
	cd python && python ./setup.py install


.PHONY: clean

clean:
	rm libfisheye.so
	rm -rf python/build python/__pycache__ python/dist

install: libfisheye.so
	install $< /usr/lib/
