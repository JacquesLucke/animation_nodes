#!/bin/sh
set -e

gcc -c FastNoiseSIMD.cpp -std=c++11 -fPIC -O3
gcc -c FastNoiseSIMD_internal.cpp -std=c++11 -fPIC -O3

if [ "$(arch)" == "arm64" ]; then
	gcc -c FastNoiseSIMD_neon.cpp -std=c++11 -fPIC -O3
else
	gcc -c FastNoiseSIMD_sse2.cpp -std=c++11 -fPIC -O3 -msse2
	gcc -c FastNoiseSIMD_sse41.cpp -std=c++11 -fPIC -O3 -msse4.1
	gcc -c FastNoiseSIMD_avx2.cpp -std=c++11 -fPIC -O3 -march=core-avx2
fi

ar rcs libFastNoiseSIMD_macos.a *.o

echo "Done."
