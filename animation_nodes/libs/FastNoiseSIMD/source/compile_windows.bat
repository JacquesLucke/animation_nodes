:: Please run this file in the 'x64 Native Tools Command Prompt for VS 2017'
:: If you don't have it, install Visual Studio 2017
@echo off
setlocal

:: -c      Create only .obj file
:: /EHsc   Set appropriate error handling
:: /GL-    Disable whole program optimization
:: /Ox     Enable full optimization
set args=-c /EHsc /GL- /Ox

cl FastNoiseSIMD.cpp %args%
cl FastNoiseSIMD_internal.cpp %args%
cl FastNoiseSIMD_sse2.cpp %args%
cl FastNoiseSIMD_sse41.cpp %args%
cl FastNoiseSIMD_avx2.cpp %args% /arch:AVX2

lib *.obj /OUT:FastNoiseSIMD_windows.lib

@echo Done.
