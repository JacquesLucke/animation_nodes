cd "${0%/*}"
gcc -c FastNoiseSIMD.cpp -std=c++11 -fPIC -O3
gcc -c FastNoiseSIMD_internal.cpp -std=c++11 -fPIC -O3
gcc -c FastNoiseSIMD_sse2.cpp -std=c++11 -fPIC -O3 -msse2
gcc -c FastNoiseSIMD_sse41.cpp -std=c++11 -fPIC -O3 -msse4.1
gcc -c FastNoiseSIMD_avx2.cpp -std=c++11 -fPIC -O3 -march=core-avx2
ar rcs libFastNoiseSIMD_linux.a *.o

echo "Done."
