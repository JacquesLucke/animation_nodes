WHERE cl >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo cl command not found
    echo Only tested in 'x64 Native Tools Command Prompt for VS 2017'
    exit
)

cl FastNoiseSIMD.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_internal.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_sse2.cpp -c /EHsc /GL- /Ox
cl FastNoiseSIMD_sse41.cpp -c /EHsc /GL- /Ox
lib FastNoiseSIMD.obj FastNoiseSIMD_sse2.obj FastNoiseSIMD_sse41.obj /OUT:FastNoiseSIMD.lib

copy FastNoiseSIMD.h ..\FastNoiseSIMD.h
copy FastNoiseSIMD.lib ..\FastNoiseSIMD.lib
