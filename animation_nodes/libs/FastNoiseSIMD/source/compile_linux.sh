gcc -c FastNoiseSIMD.cpp -std=c++11 -fPIC -O3
gcc -c FastNoiseSIMD_internal.cpp -std=c++11 -fPIC -O3
gcc -c FastNoiseSIMD_sse2.cpp -std=c++11 -fPIC -O3 -msse2
gcc -c FastNoiseSIMD_sse41.cpp -std=c++11 -fPIC -O3 -msse4.1
gcc -c FastNoiseSIMD_avx2.cpp -std=c++11 -fPIC -O3 -march=core-avx2
ar rcs libFastNoiseSIMD.a *.o
cp FastNoiseSIMD.h ../FastNoiseSIMD.h
cp libFastNoiseSIMD.a ../libFastNoiseSIMD.a
echo "Done."
