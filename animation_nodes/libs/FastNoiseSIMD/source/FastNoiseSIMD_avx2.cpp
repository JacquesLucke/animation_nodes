// FastNoiseSIMD_avx2.cpp
//
// MIT License
//
// Copyright(c) 2017 Jordan Peck
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files(the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// The developer's email is jorzixdan.me2@gzixmail.com (for great email, take
// off every 'zix'.)
//

#include "FastNoiseSIMD.h"

// DISABLE WHOLE PROGRAM OPTIMIZATION for this file when using MSVC

// To compile AVX2 support enable AVX(2) code generation compiler flags for this file
#ifdef FN_COMPILE_AVX2
#ifndef __AVX__
#ifdef __GNUC__
#error To compile AVX2 add build command "-march=core-avx2" on FastNoiseSIMD_avx2.cpp, or remove "#define FN_COMPILE_AVX2" from FastNoiseSIMD.h
#else
#error To compile AVX2 set C++ code generation to use /arch:AVX(2) on FastNoiseSIMD_avx2.cpp, or remove "#define FN_COMPILE_AVX2" from FastNoiseSIMD.h
#endif
#endif

#define SIMD_LEVEL_H FN_AVX2
#include "FastNoiseSIMD_internal.h"
#include <immintrin.h> //AVX2 FMA3

#define SIMD_LEVEL FN_AVX2
#include "FastNoiseSIMD_internal.cpp"
#endif