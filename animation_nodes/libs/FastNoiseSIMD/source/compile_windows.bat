:: Please run this file in the 'x64 Native Tools Command Prompt for VS 2017'
:: If you don't have it, install Visual Studio 2017

cl FastNoiseSIMD.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_internal.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_sse2.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_sse41.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_avx2.cpp -c /EHsc /GL- /Ox /arch:AVX2
lib *.obj /OUT:FastNoiseSIMD_windows.lib

@echo Done.
