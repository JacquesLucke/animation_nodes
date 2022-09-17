#!/bin/sh

# copied from file compile_macos.sh
# on OpenBSD `pkg_info -L gcc` - gcc installs as /usr/local/bin/egcc

set -e

egcc -c FastNoiseSIMD.cpp -std=c++11 -fPIC -O3
egcc -c FastNoiseSIMD_internal.cpp -std=c++11 -fPIC -O3

if [ "$(arch)" == "arm64" ]; then
	egcc -c FastNoiseSIMD_neon.cpp -std=c++11 -fPIC -O3
else
	egcc -c FastNoiseSIMD_sse2.cpp -std=c++11 -fPIC -O3 -msse2
	egcc -c FastNoiseSIMD_sse41.cpp -std=c++11 -fPIC -O3 -msse4.1
	egcc -c FastNoiseSIMD_avx2.cpp -std=c++11 -fPIC -O3 -march=core-avx2
fi

egcc-ar rcs libFastNoiseSIMD_openbsd.a *.o

echo "Done."
