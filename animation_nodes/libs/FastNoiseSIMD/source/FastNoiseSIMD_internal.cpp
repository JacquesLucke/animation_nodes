// FastNoiseSIMD_internal.cpp
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
#include <assert.h> 

#if defined(SIMD_LEVEL) || defined(FN_COMPILE_NO_SIMD_FALLBACK)

#ifndef SIMD_LEVEL
#define SIMD_LEVEL FN_NO_SIMD_FALLBACK
#define SIMD_LEVEL_H FN_NO_SIMD_FALLBACK
#include "FastNoiseSIMD_internal.h"
#include <math.h>
#define FN_ALIGNED_SETS
#endif

// Per SIMD level var/function naming
#define L_VAR2(x, l) L##l##_##x
#define L_VAR(x, l) L_VAR2(x, l)
#define VAR(x) L_VAR(x, SIMD_LEVEL)
#define FUNC(x) VAR(FUNC_##x)
#define SIMDf_NUM(n) VAR(SIMDf_NUM_##n)
#define SIMDi_NUM(n) VAR(SIMDi_NUM_##n)

#define SIMD_LEVEL_CLASS FastNoiseSIMD_internal::FASTNOISE_SIMD_CLASS(SIMD_LEVEL)

#if defined(_WIN32) && SIMD_LEVEL > FN_NO_SIMD_FALLBACK
#define VECTORCALL __vectorcall
#else
#define VECTORCALL
#endif

// Typedefs
#if SIMD_LEVEL == FN_NEON
#define VECTOR_SIZE 4
#define MEMORY_ALIGNMENT 16
typedef float32x4_t SIMDf;
typedef int32x4_t SIMDi;
#define SIMDf_SET(a) vdupq_n_f32(a)
#define SIMDf_SET_ZERO() vdupq_n_f32(0)
#define SIMDi_SET(a) vdupq_n_s32(a)
#define SIMDi_SET_ZERO() vdupq_n_s32(0)

#elif SIMD_LEVEL == FN_AVX512
#define VECTOR_SIZE 16
#define MEMORY_ALIGNMENT 64
typedef __m512 SIMDf;
typedef __m512i SIMDi;
#define SIMDf_SET(a) _mm512_set1_ps(a)
#define SIMDf_SET_ZERO() _mm512_setzero_ps()
#define SIMDi_SET(a) _mm512_set1_epi32(a)
#define SIMDi_SET_ZERO() _mm512_setzero_si512()

#elif SIMD_LEVEL == FN_AVX2
#define VECTOR_SIZE 8
#define MEMORY_ALIGNMENT 32
typedef __m256 SIMDf;
typedef __m256i SIMDi;
#define SIMDf_SET(a) _mm256_set1_ps(a)
#define SIMDf_SET_ZERO() _mm256_setzero_ps()
#define SIMDi_SET(a) _mm256_set1_epi32(a)
#define SIMDi_SET_ZERO() _mm256_setzero_si256()

#elif SIMD_LEVEL >= FN_SSE2
#define VECTOR_SIZE 4
#define MEMORY_ALIGNMENT 16
typedef __m128 SIMDf;
typedef __m128i SIMDi;
#define SIMDf_SET(a) _mm_set1_ps(a)
#define SIMDf_SET_ZERO() _mm_setzero_ps()
#define SIMDi_SET(a) _mm_set1_epi32(a)
#define SIMDi_SET_ZERO() _mm_setzero_si128()

#else // Fallback to float/int
#define VECTOR_SIZE 1
#define MEMORY_ALIGNMENT 4
typedef float SIMDf;
typedef int SIMDi;
#define SIMDf_SET(a) (a)
#define SIMDf_SET_ZERO() (0)
#define SIMDi_SET(a) (a)
#define SIMDi_SET_ZERO() (0)
#endif

// Memory Allocation
#if SIMD_LEVEL > FN_NO_SIMD_FALLBACK && defined(FN_ALIGNED_SETS)
#ifdef _WIN32
#define SIMD_ALLOCATE_SET(floatP, floatCount) floatP = (float*)_aligned_malloc((floatCount)* sizeof(float), MEMORY_ALIGNMENT)
#else
#define SIMD_ALLOCATE_SET(floatP, floatCount) posix_memalign((void**)&floatP, MEMORY_ALIGNMENT, (floatCount)* sizeof(float))
#endif
#else
#define SIMD_ALLOCATE_SET(floatP, floatCount) floatP = new float[floatCount]
#endif

union uSIMDf
{
	SIMDf m;
	float a[VECTOR_SIZE];
};

union uSIMDi
{
	SIMDi m;
	int a[VECTOR_SIZE];
};

#if SIMD_LEVEL == FN_AVX512
typedef __mmask16 MASK;
#else
typedef SIMDi MASK;
#endif


static SIMDi SIMDi_NUM(0xffffffff);
static SIMDf SIMDf_NUM(1);

// SIMD functions
#if SIMD_LEVEL == FN_NEON

#define SIMDf_STORE(p,a) vst1q_f32(p, a)
#define SIMDf_LOAD(p) vld1q_f32(p)

#define SIMDf_UNDEFINED() SIMDf_SET(0)
#define SIMDi_UNDEFINED() SIMDi_SET(0)

#define SIMDf_CONVERT_TO_FLOAT(a) vcvtq_f32_s32(a)
#define SIMDf_CAST_TO_FLOAT(a) vreinterpretq_f32_s32(a)
#define SIMDi_CONVERT_TO_INT(a) vcvtq_s32_f32(a)
#define SIMDi_CAST_TO_INT(a) vreinterpretq_s32_f32(a)

#define SIMDf_ADD(a,b) vaddq_f32(a,b)
#define SIMDf_SUB(a,b) vsubq_f32(a,b)
#define SIMDf_MUL(a,b) vmulq_f32(a,b)
#define SIMDf_DIV(a,b) FUNC(DIV)(a,b)

static SIMDf VECTORCALL FUNC(DIV)(SIMDf a, SIMDf b)
{
	SIMDf reciprocal = vrecpeq_f32(b);
	// use a couple Newton-Raphson steps to refine the estimate.  Depending on your
	// application's accuracy requirements, you may be able to get away with only
	// one refinement (instead of the two used here).  Be sure to test!
	reciprocal = vmulq_f32(vrecpsq_f32(b, reciprocal), reciprocal);

	// and finally, compute a/b = a*(1/b)
	return vmulq_f32(a, reciprocal);
}

#define SIMDf_MIN(a,b) vminq_f32(a,b)
#define SIMDf_MAX(a,b) vmaxq_f32(a,b)
#define SIMDf_INV_SQRT(a) vrsqrteq_f32(a)

#define SIMDf_LESS_THAN(a,b) vreinterpretq_f32_u32(vcltq_f32(a,b))
#define SIMDf_GREATER_THAN(a,b) vreinterpretq_f32_u32(vcgtq_f32(a,b))
#define SIMDf_LESS_EQUAL(a,b) vreinterpretq_f32_u32(vcleq_f32(a,b))
#define SIMDf_GREATER_EQUAL(a,b) vreinterpretq_f32_u32(vcgeq_f32(a,b))

#define SIMDf_AND(a,b) SIMDf_CAST_TO_FLOAT(vandq_s32(vreinterpretq_s32_f32(a),vreinterpretq_s32_f32(b)))
#define SIMDf_AND_NOT(a,b) SIMDf_CAST_TO_FLOAT(vandq_s32(vmvnq_s32(vreinterpretq_s32_f32(a)),vreinterpretq_s32_f32(b)))
#define SIMDf_XOR(a,b) SIMDf_CAST_TO_FLOAT(veorq_s32(vreinterpretq_s32_f32(a),vreinterpretq_s32_f32(b)))

#ifndef __aarch64__
static SIMDf VECTORCALL FUNC(FLOOR)(SIMDf a)
{
	SIMDf fval = SIMDf_CONVERT_TO_FLOAT(SIMDi_CONVERT_TO_INT(a));

	return vsubq_f32(fval, SIMDf_AND(SIMDf_LESS_THAN(a, fval), SIMDf_NUM(1)));
}
#define SIMDf_FLOOR(a) FUNC(FLOOR)(a)
#else

#define SIMDf_FLOOR(a) vrndmq_f32(a)
#endif

#define SIMDf_ABS(a) vabsq_f32(a)
#define SIMDf_BLENDV(a,b,mask) vbslq_f32(mask,b,a)

#define SIMDi_ADD(a,b) vaddq_s32(a,b)
#define SIMDi_SUB(a,b) vsubq_s32(a,b)
#define SIMDi_MUL(a,b) vmulq_s32(a,b)

#define SIMDi_AND(a,b) vandq_s32(a,b)
#define SIMDi_AND_NOT(a,b) vandq_s32(vmvnq_s32(a),b)
#define SIMDi_OR(a,b) vorrq_s32(a,b)
#define SIMDi_XOR(a,b) veorq_s32(a,b)
#define SIMDi_NOT(a) vmvnq_s32(a)

#define SIMDi_SHIFT_R(a, b) vshrq_n_s32(a, b)
#define SIMDi_SHIFT_L(a, b) vshlq_n_s32(a, b)
#define SIMDi_VSHIFT_L(a, b) vshlq_s32(a, b)

#define SIMDi_EQUAL(a,b) vreinterpretq_s32_u32(vceqq_s32(a,b))
#define SIMDi_GREATER_THAN(a,b) vreinterpretq_s32_u32(vcgtq_s32(a,b))
#define SIMDi_LESS_THAN(a,b) vreinterpretq_s32_u32(vcltq_s32(a,b))

#elif SIMD_LEVEL == FN_AVX512

#ifdef FN_ALIGNED_SETS
#define SIMDf_STORE(p,a) _mm512_store_ps(p,a)
#define SIMDf_LOAD(p) _mm512_load_ps(p)
#else
#define SIMDf_STORE(p,a) _mm512_storeu_ps(p,a)
#define SIMDf_LOAD(p) _mm512_loadu_ps(p)
#endif

#define SIMDf_UNDEFINED() _mm512_undefined_ps()
#define SIMDi_UNDEFINED() _mm512_undefined_epi32()

#define SIMDf_ADD(a,b) _mm512_add_ps(a,b)
#define SIMDf_SUB(a,b) _mm512_sub_ps(a,b)
#define SIMDf_MUL(a,b) _mm512_mul_ps(a,b)
#define SIMDf_DIV(a,b) _mm512_div_ps(a,b)

#define SIMDf_MIN(a,b) _mm512_min_ps(a,b)
#define SIMDf_MAX(a,b) _mm512_max_ps(a,b)
#define SIMDf_INV_SQRT(a) _mm512_rsqrt14_ps(a)

#define SIMDf_LESS_THAN(a,b) _mm512_cmp_ps_mask(a,b,_CMP_LT_OQ)
#define SIMDf_GREATER_THAN(a,b) _mm512_cmp_ps_mask(a,b,_CMP_GT_OQ)
#define SIMDf_LESS_EQUAL(a,b) _mm512_cmp_ps_mask(a,b,_CMP_LE_OQ)
#define SIMDf_GREATER_EQUAL(a,b) _mm512_cmp_ps_mask(a,b,_CMP_GE_OQ)

#define SIMDf_AND(a,b) _mm512_and_ps(a,b)
#define SIMDf_AND_NOT(a,b) _mm512_andnot_ps(a,b)
#define SIMDf_XOR(a,b) _mm512_xor_ps(a,b)

#define SIMDf_FLOOR(a) _mm512_floor_ps(a)
#define SIMDf_ABS(a) _mm512_abs_ps(a)
#define SIMDf_BLENDV(a,b,mask) _mm512_mask_blend_ps(mask,a,b)
#define SIMDf_GATHER(p,a) _mm512_i32gather_ps(a,p,4)
#define SIMDf_PERMUTE(a,b) _mm512_permutexvar_ps(b,a)

#define SIMDi_ADD(a,b) _mm512_add_epi32(a,b)
#define SIMDi_SUB(a,b) _mm512_sub_epi32(a,b)
#define SIMDi_MUL(a,b) _mm512_mullo_epi32(a,b)

#define SIMDi_AND(a,b) _mm512_and_si512(a,b)
#define SIMDi_AND_NOT(a,b) _mm512_andnot_si512(a,b)
#define SIMDi_OR(a,b) _mm512_or_si512(a,b)
#define SIMDi_XOR(a,b) _mm512_xor_si512(a,b)
#define SIMDi_NOT(a) SIMDi_XOR(a,SIMDi_NUM(0xffffffff))

#define SIMDi_SHIFT_R(a, b) _mm512_srai_epi32(a, b)
#define SIMDi_SHIFT_L(a, b) _mm512_slli_epi32(a, b)

#define SIMDi_VSHIFT_R(a,b) _mm512_srl_epi32(a, b)
#define SIMDi_VSHIFT_L(a,b) _mm512_sll_epi32(a, b)

#define SIMDi_EQUAL(a,b) _mm512_cmpeq_epi32_mask(a,b)
#define SIMDi_GREATER_THAN(a,b) _mm512_cmpgt_epi32_mask(a,b)
#define SIMDi_LESS_THAN(a,b) _mm512_cmpgt_epi32_mask(b,a)

#define SIMDf_CONVERT_TO_FLOAT(a) _mm512_cvtepi32_ps(a)
#define SIMDf_CAST_TO_FLOAT(a) _mm512_castsi512_ps(a)
#define SIMDi_CONVERT_TO_INT(a) _mm512_cvtps_epi32(a)
#define SIMDi_CAST_TO_INT(a) _mm512_castps_si512(a)

#elif SIMD_LEVEL == FN_AVX2

#ifdef FN_ALIGNED_SETS
#define SIMDf_STORE(p,a) _mm256_store_ps(p,a)
#define SIMDf_LOAD(p) _mm256_load_ps(p)
#else
#define SIMDf_STORE(p,a) _mm256_storeu_ps(p,a)
#define SIMDf_LOAD(p) _mm256_loadu_ps(p)
#endif

#define SIMDf_UNDEFINED() _mm256_undefined_ps()
#define SIMDi_UNDEFINED() _mm256_undefined_si256()

#define SIMDf_CONVERT_TO_FLOAT(a) _mm256_cvtepi32_ps(a)
#define SIMDf_CAST_TO_FLOAT(a) _mm256_castsi256_ps(a)
#define SIMDi_CONVERT_TO_INT(a) _mm256_cvtps_epi32(a)
#define SIMDi_CAST_TO_INT(a) _mm256_castps_si256(a)

#define SIMDf_ADD(a,b) _mm256_add_ps(a,b)
#define SIMDf_SUB(a,b) _mm256_sub_ps(a,b)
#define SIMDf_MUL(a,b) _mm256_mul_ps(a,b)
#define SIMDf_DIV(a,b) _mm256_div_ps(a,b)

#define SIMDf_MIN(a,b) _mm256_min_ps(a,b)
#define SIMDf_MAX(a,b) _mm256_max_ps(a,b)
#define SIMDf_INV_SQRT(a) _mm256_rsqrt_ps(a)

#define SIMDf_LESS_THAN(a,b) SIMDi_CAST_TO_INT(_mm256_cmp_ps(a,b,_CMP_LT_OQ))
#define SIMDf_GREATER_THAN(a,b) SIMDi_CAST_TO_INT(_mm256_cmp_ps(a,b,_CMP_GT_OQ))
#define SIMDf_LESS_EQUAL(a,b) SIMDi_CAST_TO_INT(_mm256_cmp_ps(a,b,_CMP_LE_OQ))
#define SIMDf_GREATER_EQUAL(a,b) SIMDi_CAST_TO_INT( _mm256_cmp_ps(a,b,_CMP_GE_OQ))

#define SIMDf_AND(a,b) _mm256_and_ps(a,b)
#define SIMDf_AND_NOT(a,b) _mm256_andnot_ps(a,b)
#define SIMDf_XOR(a,b) _mm256_xor_ps(a,b)

#define SIMDf_FLOOR(a) _mm256_floor_ps(a)
#define SIMDf_ABS(a) SIMDf_AND(a,SIMDf_CAST_TO_FLOAT(SIMDi_NUM(0x7fffffff)))
#define SIMDf_BLENDV(a,b,mask) _mm256_blendv_ps(a,b,SIMDf_CAST_TO_FLOAT(mask))
#define SIMDf_PERMUTE(a,b) _mm256_permutevar8x32_ps(a,b)

#define SIMDi_ADD(a,b) _mm256_add_epi32(a,b)
#define SIMDi_SUB(a,b) _mm256_sub_epi32(a,b)
#define SIMDi_MUL(a,b) _mm256_mullo_epi32(a,b)

#define SIMDi_AND(a,b) _mm256_and_si256(a,b)
#define SIMDi_AND_NOT(a,b) _mm256_andnot_si256(a,b)
#define SIMDi_OR(a,b) _mm256_or_si256(a,b)
#define SIMDi_XOR(a,b) _mm256_xor_si256(a,b)
#define SIMDi_NOT(a) SIMDi_XOR(a,SIMDi_NUM(0xffffffff))

#define SIMDi_SHIFT_R(a, b) _mm256_srai_epi32(a, b)
#define SIMDi_SHIFT_L(a, b) _mm256_slli_epi32(a, b)

#define SIMDi_EQUAL(a,b) _mm256_cmpeq_epi32(a,b)
#define SIMDi_GREATER_THAN(a,b) _mm256_cmpgt_epi32(a,b)
#define SIMDi_LESS_THAN(a,b) _mm256_cmpgt_epi32(b,a)

#elif SIMD_LEVEL >= FN_SSE2

#ifdef FN_ALIGNED_SETS
#define SIMDf_STORE(p,a) _mm_store_ps(p,a)
#define SIMDf_LOAD(p) _mm_load_ps(p)
#else
#define SIMDf_STORE(p,a) _mm_storeu_ps(p,a)
#define SIMDf_LOAD(p) _mm_loadu_ps(p)
#endif

#define SIMDf_UNDEFINED() SIMDf_SET_ZERO()
#define SIMDi_UNDEFINED() SIMDi_SET_ZERO()

#define SIMDf_CONVERT_TO_FLOAT(a) _mm_cvtepi32_ps(a)
#define SIMDf_CAST_TO_FLOAT(a) _mm_castsi128_ps(a)
#define SIMDi_CONVERT_TO_INT(a) _mm_cvtps_epi32(a)
#define SIMDi_CAST_TO_INT(a) _mm_castps_si128(a)

#define SIMDf_ADD(a,b) _mm_add_ps(a,b)
#define SIMDf_SUB(a,b) _mm_sub_ps(a,b)
#define SIMDf_MUL(a,b) _mm_mul_ps(a,b)
#define SIMDf_DIV(a,b) _mm_div_ps(a,b)

#define SIMDf_MIN(a,b) _mm_min_ps(a,b)
#define SIMDf_MAX(a,b) _mm_max_ps(a,b)
#define SIMDf_INV_SQRT(a) _mm_rsqrt_ps(a)

#define SIMDf_LESS_THAN(a,b) SIMDi_CAST_TO_INT(_mm_cmplt_ps(a,b))
#define SIMDf_GREATER_THAN(a,b) SIMDi_CAST_TO_INT(_mm_cmpgt_ps(a,b))
#define SIMDf_LESS_EQUAL(a,b) SIMDi_CAST_TO_INT(_mm_cmple_ps(a,b))
#define SIMDf_GREATER_EQUAL(a,b) SIMDi_CAST_TO_INT(_mm_cmpge_ps(a,b))

#define SIMDf_AND(a,b) _mm_and_ps(a,b)
#define SIMDf_AND_NOT(a,b) _mm_andnot_ps(a,b)
#define SIMDf_XOR(a,b) _mm_xor_ps(a,b)

#define SIMDf_ABS(a) SIMDf_AND(a,SIMDf_CAST_TO_FLOAT(SIMDi_NUM(0x7fffffff)))

#if SIMD_LEVEL == FN_SSE41
#define SIMDi_MUL(a,b) _mm_mullo_epi32(a,b)
#define SIMDf_FLOOR(a) _mm_floor_ps(a)
#define SIMDf_BLENDV(a,b,mask) _mm_blendv_ps(a,b,SIMDf_CAST_TO_FLOAT(mask))
#else
static SIMDi VECTORCALL FUNC(MUL)(SIMDi a, SIMDi b)
{
	__m128 tmp1 = _mm_castsi128_ps(_mm_mul_epu32(a, b)); /* mul 2,0*/
	__m128 tmp2 = _mm_castsi128_ps(_mm_mul_epu32(_mm_srli_si128(a, 4), _mm_srli_si128(b, 4))); /* mul 3,1 */
	return _mm_shuffle_epi32(_mm_castps_si128(_mm_shuffle_ps(tmp1, tmp2, _MM_SHUFFLE(2, 0, 2, 0))), _MM_SHUFFLE(3, 1, 2, 0));
}
#define SIMDi_MUL(a,b) FUNC(MUL)(a,b)

static SIMDf VECTORCALL FUNC(FLOOR)(SIMDf a)
{
	__m128 fval = _mm_cvtepi32_ps(_mm_cvttps_epi32(a));

	return _mm_sub_ps(fval, _mm_and_ps(_mm_cmplt_ps(a, fval), SIMDf_NUM(1)));
}
#define SIMDf_FLOOR(a) FUNC(FLOOR)(a)

#define SIMDf_BLENDV(a,b,mask) _mm_or_ps(_mm_andnot_ps(SIMDf_CAST_TO_FLOAT(mask), a), _mm_and_ps(SIMDf_CAST_TO_FLOAT(mask), b))
#endif

#define SIMDi_ADD(a,b) _mm_add_epi32(a,b)
#define SIMDi_SUB(a,b) _mm_sub_epi32(a,b)

#define SIMDi_AND(a,b) _mm_and_si128(a,b)
#define SIMDi_AND_NOT(a,b) _mm_andnot_si128(a,b)
#define SIMDi_OR(a,b) _mm_or_si128(a,b)
#define SIMDi_XOR(a,b) _mm_xor_si128(a,b)
#define SIMDi_NOT(a) SIMDi_XOR(a,SIMDi_NUM(0xffffffff))

#define SIMDi_SHIFT_R(a,b) _mm_srai_epi32(a, b)
#define SIMDi_SHIFT_L(a,b) _mm_slli_epi32(a, b)

#define SIMDi_EQUAL(a,b) _mm_cmpeq_epi32(a,b)
#define SIMDi_GREATER_THAN(a,b) _mm_cmpgt_epi32(a,b)
#define SIMDi_LESS_THAN(a,b) _mm_cmpgt_epi32(b,a)

#else // Fallback

static int FUNC(CAST_TO_INT)(float f) { return *reinterpret_cast<int*>(&f); }
static float FUNC(CAST_TO_FLOAT)(int i) { return *reinterpret_cast<float*>(&i); }
#define SIMDi_CAST_TO_INT(a) FUNC(CAST_TO_INT)(a)
#define SIMDf_CAST_TO_FLOAT(a) FUNC(CAST_TO_FLOAT)(a)

#define SIMDf_STORE(p,a) (*(p) = a)
#define SIMDf_LOAD(p) (*p)

#define SIMDf_UNDEFINED() (0)
#define SIMDi_UNDEFINED() (0)

#define SIMDf_ADD(a,b) ((a) + (b))
#define SIMDf_SUB(a,b) ((a) - (b))
#define SIMDf_MUL(a,b) ((a) * (b))
#define SIMDf_DIV(a,b) ((a) / (b))

#define SIMDf_MIN(a,b) fminf(a,b)
#define SIMDf_MAX(a,b) fmaxf(a,b)

static float FUNC(INV_SQRT)(float x)
{
	float xhalf = 0.5f * x;
	int i = *(int*)&x;
	i = 0x5f3759df - (i >> 1);
	x = *(float*)&i;
	x = x*(1.5f - xhalf*x*x);
	return x;
}
#define SIMDf_INV_SQRT(a) FUNC(INV_SQRT)(a)

#define SIMDf_LESS_THAN(a,b) (((a) < (b)) ? 0xFFFFFFFF : 0)
#define SIMDf_GREATER_THAN(a,b) (((a) > (b)) ? 0xFFFFFFFF : 0)
#define SIMDf_LESS_EQUAL(a,b) (((a) <= (b)) ? 0xFFFFFFFF : 0)
#define SIMDf_GREATER_EQUAL(a,b) (((a) >= (b)) ? 0xFFFFFFFF : 0)

#define SIMDf_AND(a,b) SIMDf_CAST_TO_FLOAT(SIMDi_CAST_TO_INT(a) & SIMDi_CAST_TO_INT(b))
#define SIMDf_AND_NOT(a,b) SIMDf_CAST_TO_FLOAT(~SIMDi_CAST_TO_INT(a) & SIMDi_CAST_TO_INT(b))
#define SIMDf_XOR(a,b) SIMDf_CAST_TO_FLOAT(SIMDi_CAST_TO_INT(a) ^ SIMDi_CAST_TO_INT(b))

#define SIMDf_FLOOR(a) floorf(a)
#define SIMDf_ABS(a) fabsf(a)
#define SIMDf_BLENDV(a,b,mask) (mask ? (b) : (a))
#define SIMDf_GATHER(p,a) (*(reinterpret_cast<const float*>(p)+(a)))

#define SIMDi_ADD(a,b) ((a) + (b))
#define SIMDi_SUB(a,b) ((a) - (b))
#define SIMDi_MUL(a,b) ((a) * (b))

#define SIMDi_AND(a,b) ((a) & (b))
#define SIMDi_AND_NOT(a,b) (~(a) & (b))
#define SIMDi_OR(a,b) ((a) | (b))
#define SIMDi_XOR(a,b) ((a) ^ (b))
#define SIMDi_NOT(a) (~(a))

#define SIMDi_SHIFT_R(a, b) ((a) >> (b))
#define SIMDi_SHIFT_L(a, b) ((a) << (b))

#define SIMDi_EQUAL(a,b) (((a) == (b)) ? 0xFFFFFFFF : 0)
#define SIMDi_GREATER_THAN(a,b) (((a) > (b)) ? 0xFFFFFFFF : 0)
#define SIMDi_LESS_THAN(a,b) (((a) < (b)) ? 0xFFFFFFFF : 0)

#define SIMDi_CONVERT_TO_INT(a) static_cast<int>(roundf(a))
#define SIMDf_CONVERT_TO_FLOAT(a) static_cast<float>(a)
#endif

//#define SIMDf_SIGN_FLIP(a) SIMDf_XOR(a,SIMDf_NUM(neg0)))
//#define SIMDi_GREATER_EQUAL(a,b) SIMDi_NOT(SIMDi_LESS_THAN(a,b))
//#define SIMDi_LESS_EQUAL(a,b) SIMDi_NOT(SIMDi_GREATER_THAN(a,b))
//#define SIMDi_BLENDV(a,b, mask) SIMDi_CAST_TO_INT(SIMDf_BLENDV(SIMDf_CAST_TO_FLOAT(a),SIMDf_CAST_TO_FLOAT(b),SIMDf_CAST_TO_FLOAT(mask)))

#if SIMD_LEVEL == FN_AVX512

#define MASK_OR(a,b) ((a)|(b))
#define MASK_AND(a,b) ((a)&(b))
#define MASK_AND_NOT(a,b) (~(a)&(b))
#define MASK_NOT(a) (~(a))

#define SIMDf_MASK(m,a) _mm512_maskz_mov_ps(m,a)
#define SIMDf_MASK_ADD(m,a,b) _mm512_mask_add_ps(a,m,a,b)
#define SIMDf_MASK_SUB(m,a,b) _mm512_mask_sub_ps(a,m,a,b)

#define SIMDi_MASK_ADD(m,a,b) _mm512_mask_add_epi32(a,m,a,b)
#define SIMDi_MASK_SUB(m,a,b) _mm512_mask_sub_epi32(a,m,a,b)

#else

#define MASK_OR(a,b) SIMDi_OR(a,b)
#define MASK_AND(a,b) SIMDi_AND(a,b)
#define MASK_AND_NOT(a,b) SIMDi_AND_NOT(a,b)
#define MASK_NOT(a) SIMDi_NOT(a)

#define SIMDf_MASK(m,a) SIMDf_AND(SIMDf_CAST_TO_FLOAT(m),a)
#define SIMDf_MASK_ADD(m,a,b) SIMDf_ADD(a,SIMDf_AND(SIMDf_CAST_TO_FLOAT(m),b))
#define SIMDf_MASK_SUB(m,a,b) SIMDf_SUB(a,SIMDf_AND(SIMDf_CAST_TO_FLOAT(m),b))

#define SIMDi_MASK_ADD(m,a,b) SIMDi_ADD(a,SIMDi_AND(m,b))
#define SIMDi_MASK_SUB(m,a,b) SIMDi_SUB(a,SIMDi_AND(m,b))

#endif

#if SIMD_LEVEL == FN_AVX512
#elif SIMD_LEVEL == FN_NEON
#elif SIMD_LEVEL == FN_NO_SIMD_FALLBACK
#else
#endif

#if SIMD_LEVEL == FN_AVX2
#define SIMD_ZERO_ALL() //_mm256_zeroall()
#else
#define SIMD_ZERO_ALL()
#endif

// FMA
#ifdef FN_USE_FMA
#if SIMD_LEVEL == FN_NEON
#define SIMDf_MUL_ADD(a,b,c) vmlaq_f32(b,c,a)
#define SIMDf_MUL_SUB(a,b,c) SIMDf_SUB(SIMDf_MUL(a,b),c) // Neon multiply sub swaps sides of minus compared to FMA making it unusable
#define SIMDf_NMUL_ADD(a,b,c) vmlaq_f32(b,c,a)
#elif SIMD_LEVEL == FN_AVX512
#define SIMDf_MUL_ADD(a,b,c) _mm512_fmadd_ps(a,b,c)
#define SIMDf_MUL_SUB(a,b,c) _mm512_fmsub_ps(a,b,c)
#define SIMDf_NMUL_ADD(a,b,c) _mm512_fnmadd_ps(a,b,c)
#elif SIMD_LEVEL == FN_AVX2
#define SIMDf_MUL_ADD(a,b,c) _mm256_fmadd_ps(a,b,c)
#define SIMDf_MUL_SUB(a,b,c) _mm256_fmsub_ps(a,b,c)
#define SIMDf_NMUL_ADD(a,b,c) _mm256_fnmadd_ps(a,b,c)
#endif
#endif

#ifndef SIMDf_MUL_ADD
#define SIMDf_MUL_ADD(a,b,c) SIMDf_ADD(SIMDf_MUL(a,b),c)
#define SIMDf_MUL_SUB(a,b,c) SIMDf_SUB(SIMDf_MUL(a,b),c)
#define SIMDf_NMUL_ADD(a,b,c)  SIMDf_SUB(c, SIMDf_MUL(a,b))
#endif

static bool VAR(SIMD_Values_Set) = false;

static SIMDf SIMDf_NUM(incremental);
static SIMDf SIMDf_NUM(0);
static SIMDf SIMDf_NUM(2);
static SIMDf SIMDf_NUM(6);
static SIMDf SIMDf_NUM(10);
static SIMDf SIMDf_NUM(15);
static SIMDf SIMDf_NUM(32);
static SIMDf SIMDf_NUM(999999);

static SIMDf SIMDf_NUM(0_5);
static SIMDf SIMDf_NUM(0_6);
static SIMDf SIMDf_NUM(15_5);
static SIMDf SIMDf_NUM(511_5);

//static SIMDf SIMDf_NUM(cellJitter);
static SIMDf SIMDf_NUM(F3);
static SIMDf SIMDf_NUM(G3);
static SIMDf SIMDf_NUM(G33);
static SIMDf SIMDf_NUM(hash2Float);
static SIMDf SIMDf_NUM(vectorSize);
static SIMDf SIMDf_NUM(cubicBounding);

#if SIMD_LEVEL == FN_AVX512
static SIMDf SIMDf_NUM(X_GRAD);
static SIMDf SIMDf_NUM(Y_GRAD);
static SIMDf SIMDf_NUM(Z_GRAD);

#else
static SIMDi SIMDi_NUM(8);
static SIMDi SIMDi_NUM(12);
static SIMDi SIMDi_NUM(13);
#endif

static SIMDi SIMDi_NUM(incremental);
static SIMDi SIMDi_NUM(1);
static SIMDi SIMDi_NUM(2);
static SIMDi SIMDi_NUM(255);
static SIMDi SIMDi_NUM(60493);
static SIMDi SIMDi_NUM(0x7fffffff);

//static SIMDi SIMDi_NUM(xGradBits);
//static SIMDi SIMDi_NUM(yGradBits);
//static SIMDi SIMDi_NUM(zGradBits);

static SIMDi SIMDi_NUM(xPrime);
static SIMDi SIMDi_NUM(yPrime);
static SIMDi SIMDi_NUM(zPrime);
static SIMDi SIMDi_NUM(bit5Mask);
static SIMDi SIMDi_NUM(bit10Mask);
static SIMDi SIMDi_NUM(vectorSize);

void FUNC(InitSIMDValues)()
{
	if (VAR(SIMD_Values_Set))
		return;

	uSIMDf incF;
	uSIMDi incI;
	for (int i = 0; i < VECTOR_SIZE; i++)
	{
		incF.a[i] = float(i);
		incI.a[i] = i;
	}
	SIMDf_NUM(incremental) = incF.m;
	SIMDi_NUM(incremental) = incI.m;

	SIMDf_NUM(0) = SIMDf_SET_ZERO();
	SIMDf_NUM(1) = SIMDf_SET(1.0f);
	SIMDf_NUM(2) = SIMDf_SET(2.0f);
	SIMDf_NUM(6) = SIMDf_SET(6.0f);
	SIMDf_NUM(10) = SIMDf_SET(10.0f);
	SIMDf_NUM(15) = SIMDf_SET(15.0f);
	SIMDf_NUM(32) = SIMDf_SET(32.0f);
	SIMDf_NUM(999999) = SIMDf_SET(999999.0f);

	SIMDf_NUM(0_5) = SIMDf_SET(0.5f);
	SIMDf_NUM(0_6) = SIMDf_SET(0.6f);
	SIMDf_NUM(15_5) = SIMDf_SET(15.5f);
	SIMDf_NUM(511_5) = SIMDf_SET(511.5f);

	//SIMDf_NUM(cellJitter) = SIMDf_SET(0.39614f);
	SIMDf_NUM(F3) = SIMDf_SET(1.f / 3.f);
	SIMDf_NUM(G3) = SIMDf_SET(1.f / 6.f);
	SIMDf_NUM(G33) = SIMDf_SET((3.f / 6.f) - 1.f);
	SIMDf_NUM(hash2Float) = SIMDf_SET(1.f / 2147483648.f);
	SIMDf_NUM(vectorSize) = SIMDf_SET(VECTOR_SIZE);
	SIMDf_NUM(cubicBounding) = SIMDf_SET(1.f / (1.5f*1.5f*1.5f));

#if SIMD_LEVEL == FN_AVX512
	SIMDf_NUM(X_GRAD) = _mm512_set_ps(0, -1, 0, 1, 0, 0, 0, 0, -1, 1, -1, 1, -1, 1, -1, 1);
	SIMDf_NUM(Y_GRAD) = _mm512_set_ps(-1, 1, -1, 1, -1, 1, -1, 1, 0, 0, 0, 0, -1, -1, 1, 1);
	SIMDf_NUM(Z_GRAD) = _mm512_set_ps(-1, 0, 1, 0, -1, -1, 1, 1, -1, -1, 1, 1, 0, 0, 0, 0);

#else
	SIMDi_NUM(8) = SIMDi_SET(8);
	SIMDi_NUM(12) = SIMDi_SET(12);
	SIMDi_NUM(13) = SIMDi_SET(13);
#endif

	SIMDi_NUM(1) = SIMDi_SET(1);
	SIMDi_NUM(2) = SIMDi_SET(2);
	SIMDi_NUM(255) = SIMDi_SET(255);
	SIMDi_NUM(60493) = SIMDi_SET(60493);
	SIMDi_NUM(0x7fffffff) = SIMDi_SET(0x7fffffff);

	//SIMDi_NUM(xGradBits) = SIMDi_SET(1683327112);
	//SIMDi_NUM(yGradBits) = SIMDi_SET(-2004331104);
	//SIMDi_NUM(zGradBits) = SIMDi_SET(-1851744171);

	SIMDi_NUM(xPrime) = SIMDi_SET(1619);
	SIMDi_NUM(yPrime) = SIMDi_SET(31337);
	SIMDi_NUM(zPrime) = SIMDi_SET(6971);
	SIMDi_NUM(bit5Mask) = SIMDi_SET(31);
	SIMDi_NUM(bit10Mask) = SIMDi_SET(1023);
	SIMDi_NUM(vectorSize) = SIMDi_SET(VECTOR_SIZE);

	SIMDi_NUM(0xffffffff) = SIMDi_SET(-1);

	VAR(SIMD_Values_Set) = true;
}

static SIMDf VECTORCALL FUNC(Lerp)(SIMDf a, SIMDf b, SIMDf t)
{
	SIMDf r;
	r = SIMDf_SUB(b, a);
	r = SIMDf_MUL_ADD(r, t, a);
	return r;
}

static SIMDf VECTORCALL FUNC(InterpQuintic)(SIMDf t)
{
	SIMDf r;
	r = SIMDf_MUL_SUB(t, SIMDf_NUM(6), SIMDf_NUM(15));
	r = SIMDf_MUL_ADD(r, t, SIMDf_NUM(10));
	r = SIMDf_MUL(r, t);
	r = SIMDf_MUL(r, t);
	r = SIMDf_MUL(r, t);

	return r;
}

static SIMDf VECTORCALL FUNC(CubicLerp)(SIMDf a, SIMDf b, SIMDf c, SIMDf d, SIMDf t)
{
	SIMDf p = SIMDf_SUB(SIMDf_SUB(d, c), SIMDf_SUB(a, b));
	return SIMDf_MUL_ADD(t, SIMDf_MUL(t, SIMDf_MUL(t, p)), SIMDf_MUL_ADD(t, SIMDf_MUL(t, SIMDf_SUB(SIMDf_SUB(a, b), p)), SIMDf_MUL_ADD(t, SIMDf_SUB(c, a), b)));
}

//static SIMDf VECTORCALL FUNC(InterpHermite)(SIMDf t)
//{
//	SIMDf r;
//	r = SIMDf_MUL(t, SIMDf_NUM(2));
//	r = SIMDf_SUB(SIMDf_ADD(SIMDf_NUM(1), SIMDf_NUM(2)), r);
//	r = SIMDf_MUL(r, t);
//	r = SIMDf_MUL(r, t);
//
//	return r;
//}

static SIMDi VECTORCALL FUNC(Hash)(SIMDi seed, SIMDi x, SIMDi y, SIMDi z)
{
	SIMDi hash = seed;

	hash = SIMDi_XOR(x, hash);
	hash = SIMDi_XOR(y, hash);
	hash = SIMDi_XOR(z, hash);

	hash = SIMDi_MUL(SIMDi_MUL(SIMDi_MUL(hash, hash), SIMDi_NUM(60493)), hash);
	hash = SIMDi_XOR(SIMDi_SHIFT_R(hash, 13), hash);

	return hash;
}

static SIMDi VECTORCALL FUNC(HashHB)(SIMDi seed, SIMDi x, SIMDi y, SIMDi z)
{
	SIMDi hash = seed;

	hash = SIMDi_XOR(x, hash);
	hash = SIMDi_XOR(y, hash);
	hash = SIMDi_XOR(z, hash);
	//hash = SIMDi_XOR(SIMDi_SHIFT_R(hash, 13), hash);

	hash = SIMDi_MUL(SIMDi_MUL(SIMDi_MUL(hash, hash), SIMDi_NUM(60493)), hash);

	return hash;
}

static SIMDf VECTORCALL FUNC(ValCoord)(SIMDi seed, SIMDi x, SIMDi y, SIMDi z)
{
	// High bit hash
	SIMDi hash = seed;

	hash = SIMDi_XOR(x, hash);
	hash = SIMDi_XOR(y, hash);
	hash = SIMDi_XOR(z, hash);

	hash = SIMDi_MUL(SIMDi_MUL(SIMDi_MUL(hash, hash), SIMDi_NUM(60493)), hash);
	//hash = SIMDi_XOR(SIMDi_SHIFT_L(hash, 13), hash);

	return SIMDf_MUL(SIMDf_NUM(hash2Float), SIMDf_CONVERT_TO_FLOAT(hash));
}

#if SIMD_LEVEL == FN_AVX512
static SIMDf VECTORCALL FUNC(GradCoord)(SIMDi seed, SIMDi xi, SIMDi yi, SIMDi zi, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDi hash = FUNC(Hash)(seed, xi, yi, zi);

	SIMDf xGrad = SIMDf_PERMUTE(SIMDf_NUM(X_GRAD), hash);
	SIMDf yGrad = SIMDf_PERMUTE(SIMDf_NUM(Y_GRAD), hash);
	SIMDf zGrad = SIMDf_PERMUTE(SIMDf_NUM(Z_GRAD), hash);

	return SIMDf_MUL_ADD(x, xGrad, SIMDf_MUL_ADD(y, yGrad, SIMDf_MUL(z, zGrad)));
}
#else
static SIMDf VECTORCALL FUNC(GradCoord)(SIMDi seed, SIMDi xi, SIMDi yi, SIMDi zi, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDi hash = FUNC(Hash)(seed, xi, yi, zi);
	SIMDi hasha13 = SIMDi_AND(hash, SIMDi_NUM(13));

	//if h < 8 then x, else y
	MASK l8 = SIMDi_LESS_THAN(hasha13, SIMDi_NUM(8));
	SIMDf u = SIMDf_BLENDV(y, x, l8);

	//if h < 4 then y else if h is 12 or 14 then x else z
	MASK l4 = SIMDi_LESS_THAN(hasha13, SIMDi_NUM(2));
	MASK h12o14 = SIMDi_EQUAL(SIMDi_NUM(12), hasha13);
	SIMDf v = SIMDf_BLENDV(SIMDf_BLENDV(z, x, h12o14), y, l4);

	//if h1 then -u else u
	//if h2 then -v else v
	SIMDf h1 = SIMDf_CAST_TO_FLOAT(SIMDi_SHIFT_L(hash, 31));
	SIMDf h2 = SIMDf_CAST_TO_FLOAT(SIMDi_SHIFT_L(SIMDi_AND(hash, SIMDi_NUM(2)), 30));
	//then add them
	return SIMDf_ADD(SIMDf_XOR(u, h1), SIMDf_XOR(v, h2));
}
#endif

static SIMDf VECTORCALL FUNC(WhiteNoiseSingle)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z)
{
	return FUNC(ValCoord)(seed,
		SIMDi_MUL(SIMDi_XOR(SIMDi_CAST_TO_INT(x), SIMDi_SHIFT_R(SIMDi_CAST_TO_INT(x), 16)), SIMDi_NUM(xPrime)),
		SIMDi_MUL(SIMDi_XOR(SIMDi_CAST_TO_INT(y), SIMDi_SHIFT_R(SIMDi_CAST_TO_INT(y), 16)), SIMDi_NUM(yPrime)),
		SIMDi_MUL(SIMDi_XOR(SIMDi_CAST_TO_INT(z), SIMDi_SHIFT_R(SIMDi_CAST_TO_INT(z), 16)), SIMDi_NUM(zPrime)));
}

static SIMDf VECTORCALL FUNC(ValueSingle)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDf xs = SIMDf_FLOOR(x);
	SIMDf ys = SIMDf_FLOOR(y);
	SIMDf zs = SIMDf_FLOOR(z);

	SIMDi x0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(xs), SIMDi_NUM(xPrime));
	SIMDi y0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(ys), SIMDi_NUM(yPrime));
	SIMDi z0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(zs), SIMDi_NUM(zPrime));
	SIMDi x1 = SIMDi_ADD(x0, SIMDi_NUM(xPrime));
	SIMDi y1 = SIMDi_ADD(y0, SIMDi_NUM(yPrime));
	SIMDi z1 = SIMDi_ADD(z0, SIMDi_NUM(zPrime));

	xs = FUNC(InterpQuintic)(SIMDf_SUB(x, xs));
	ys = FUNC(InterpQuintic)(SIMDf_SUB(y, ys));
	zs = FUNC(InterpQuintic)(SIMDf_SUB(z, zs));

	return FUNC(Lerp)(
		FUNC(Lerp)(
			FUNC(Lerp)(FUNC(ValCoord)(seed, x0, y0, z0), FUNC(ValCoord)(seed, x1, y0, z0), xs),
			FUNC(Lerp)(FUNC(ValCoord)(seed, x0, y1, z0), FUNC(ValCoord)(seed, x1, y1, z0), xs), ys),
		FUNC(Lerp)(
			FUNC(Lerp)(FUNC(ValCoord)(seed, x0, y0, z1), FUNC(ValCoord)(seed, x1, y0, z1), xs),
			FUNC(Lerp)(FUNC(ValCoord)(seed, x0, y1, z1), FUNC(ValCoord)(seed, x1, y1, z1), xs), ys), zs);
}

static SIMDf VECTORCALL FUNC(PerlinSingle)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDf xs = SIMDf_FLOOR(x);
	SIMDf ys = SIMDf_FLOOR(y);
	SIMDf zs = SIMDf_FLOOR(z);

	SIMDi x0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(xs), SIMDi_NUM(xPrime));
	SIMDi y0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(ys), SIMDi_NUM(yPrime));
	SIMDi z0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(zs), SIMDi_NUM(zPrime));
	SIMDi x1 = SIMDi_ADD(x0, SIMDi_NUM(xPrime));
	SIMDi y1 = SIMDi_ADD(y0, SIMDi_NUM(yPrime));
	SIMDi z1 = SIMDi_ADD(z0, SIMDi_NUM(zPrime));

	SIMDf xf0 = xs = SIMDf_SUB(x, xs);
	SIMDf yf0 = ys = SIMDf_SUB(y, ys);
	SIMDf zf0 = zs = SIMDf_SUB(z, zs);
	SIMDf xf1 = SIMDf_SUB(xf0, SIMDf_NUM(1));
	SIMDf yf1 = SIMDf_SUB(yf0, SIMDf_NUM(1));
	SIMDf zf1 = SIMDf_SUB(zf0, SIMDf_NUM(1));

	xs = FUNC(InterpQuintic)(xs);
	ys = FUNC(InterpQuintic)(ys);
	zs = FUNC(InterpQuintic)(zs);

	return FUNC(Lerp)(
		FUNC(Lerp)(
			FUNC(Lerp)(FUNC(GradCoord)(seed, x0, y0, z0, xf0, yf0, zf0), FUNC(GradCoord)(seed, x1, y0, z0, xf1, yf0, zf0), xs),
			FUNC(Lerp)(FUNC(GradCoord)(seed, x0, y1, z0, xf0, yf1, zf0), FUNC(GradCoord)(seed, x1, y1, z0, xf1, yf1, zf0), xs), ys),
		FUNC(Lerp)(
			FUNC(Lerp)(FUNC(GradCoord)(seed, x0, y0, z1, xf0, yf0, zf1), FUNC(GradCoord)(seed, x1, y0, z1, xf1, yf0, zf1), xs),
			FUNC(Lerp)(FUNC(GradCoord)(seed, x0, y1, z1, xf0, yf1, zf1), FUNC(GradCoord)(seed, x1, y1, z1, xf1, yf1, zf1), xs), ys), zs);
}

static SIMDf VECTORCALL FUNC(SimplexSingle)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDf f = SIMDf_MUL(SIMDf_NUM(F3), SIMDf_ADD(SIMDf_ADD(x, y), z));
	SIMDf x0 = SIMDf_FLOOR(SIMDf_ADD(x, f));
	SIMDf y0 = SIMDf_FLOOR(SIMDf_ADD(y, f));
	SIMDf z0 = SIMDf_FLOOR(SIMDf_ADD(z, f));

	SIMDi i = SIMDi_MUL(SIMDi_CONVERT_TO_INT(x0), SIMDi_NUM(xPrime));
	SIMDi j = SIMDi_MUL(SIMDi_CONVERT_TO_INT(y0), SIMDi_NUM(yPrime));
	SIMDi k = SIMDi_MUL(SIMDi_CONVERT_TO_INT(z0), SIMDi_NUM(zPrime));

	SIMDf g = SIMDf_MUL(SIMDf_NUM(G3), SIMDf_ADD(SIMDf_ADD(x0, y0), z0));
	x0 = SIMDf_SUB(x, SIMDf_SUB(x0, g));
	y0 = SIMDf_SUB(y, SIMDf_SUB(y0, g));
	z0 = SIMDf_SUB(z, SIMDf_SUB(z0, g));

	MASK x0_ge_y0 = SIMDf_GREATER_EQUAL(x0, y0);
	MASK y0_ge_z0 = SIMDf_GREATER_EQUAL(y0, z0);
	MASK x0_ge_z0 = SIMDf_GREATER_EQUAL(x0, z0);

	MASK i1 = MASK_AND(x0_ge_y0, x0_ge_z0);
	MASK j1 = MASK_AND_NOT(x0_ge_y0, y0_ge_z0);
	MASK k1 = MASK_AND_NOT(x0_ge_z0, MASK_NOT(y0_ge_z0));

	MASK i2 = MASK_OR(x0_ge_y0, x0_ge_z0);
	MASK j2 = MASK_OR(MASK_NOT(x0_ge_y0), y0_ge_z0);
	MASK k2 = MASK_NOT(MASK_AND(x0_ge_z0, y0_ge_z0));

	SIMDf x1 = SIMDf_ADD(SIMDf_MASK_SUB(i1, x0, SIMDf_NUM(1)), SIMDf_NUM(G3));
	SIMDf y1 = SIMDf_ADD(SIMDf_MASK_SUB(j1, y0, SIMDf_NUM(1)), SIMDf_NUM(G3));
	SIMDf z1 = SIMDf_ADD(SIMDf_MASK_SUB(k1, z0, SIMDf_NUM(1)), SIMDf_NUM(G3));
	SIMDf x2 = SIMDf_ADD(SIMDf_MASK_SUB(i2, x0, SIMDf_NUM(1)), SIMDf_NUM(F3));
	SIMDf y2 = SIMDf_ADD(SIMDf_MASK_SUB(j2, y0, SIMDf_NUM(1)), SIMDf_NUM(F3));
	SIMDf z2 = SIMDf_ADD(SIMDf_MASK_SUB(k2, z0, SIMDf_NUM(1)), SIMDf_NUM(F3));
	SIMDf x3 = SIMDf_ADD(x0, SIMDf_NUM(G33));
	SIMDf y3 = SIMDf_ADD(y0, SIMDf_NUM(G33));
	SIMDf z3 = SIMDf_ADD(z0, SIMDf_NUM(G33));

	SIMDf t0 = SIMDf_NMUL_ADD(z0, z0, SIMDf_NMUL_ADD(y0, y0, SIMDf_NMUL_ADD(x0, x0, SIMDf_NUM(0_6))));
	SIMDf t1 = SIMDf_NMUL_ADD(z1, z1, SIMDf_NMUL_ADD(y1, y1, SIMDf_NMUL_ADD(x1, x1, SIMDf_NUM(0_6))));
	SIMDf t2 = SIMDf_NMUL_ADD(z2, z2, SIMDf_NMUL_ADD(y2, y2, SIMDf_NMUL_ADD(x2, x2, SIMDf_NUM(0_6))));
	SIMDf t3 = SIMDf_NMUL_ADD(z3, z3, SIMDf_NMUL_ADD(y3, y3, SIMDf_NMUL_ADD(x3, x3, SIMDf_NUM(0_6))));

	MASK n0 = SIMDf_GREATER_EQUAL(t0, SIMDf_NUM(0));
	MASK n1 = SIMDf_GREATER_EQUAL(t1, SIMDf_NUM(0));
	MASK n2 = SIMDf_GREATER_EQUAL(t2, SIMDf_NUM(0));
	MASK n3 = SIMDf_GREATER_EQUAL(t3, SIMDf_NUM(0));

	t0 = SIMDf_MUL(t0, t0);
	t1 = SIMDf_MUL(t1, t1);
	t2 = SIMDf_MUL(t2, t2);
	t3 = SIMDf_MUL(t3, t3);

	SIMDf v0 = SIMDf_MUL(SIMDf_MUL(t0, t0), FUNC(GradCoord)(seed, i, j, k, x0, y0, z0));
	SIMDf v1 = SIMDf_MUL(SIMDf_MUL(t1, t1), FUNC(GradCoord)(seed, SIMDi_MASK_ADD(i1, i, SIMDi_NUM(xPrime)), SIMDi_MASK_ADD(j1, j, SIMDi_NUM(yPrime)), SIMDi_MASK_ADD(k1, k, SIMDi_NUM(zPrime)), x1, y1, z1));
	SIMDf v2 = SIMDf_MUL(SIMDf_MUL(t2, t2), FUNC(GradCoord)(seed, SIMDi_MASK_ADD(i2, i, SIMDi_NUM(xPrime)), SIMDi_MASK_ADD(j2, j, SIMDi_NUM(yPrime)), SIMDi_MASK_ADD(k2, k, SIMDi_NUM(zPrime)), x2, y2, z2));
	SIMDf v3 = SIMDf_MASK(n3, SIMDf_MUL(SIMDf_MUL(t3, t3), FUNC(GradCoord)(seed, SIMDi_ADD(i, SIMDi_NUM(xPrime)), SIMDi_ADD(j, SIMDi_NUM(yPrime)), SIMDi_ADD(k, SIMDi_NUM(zPrime)), x3, y3, z3)));

	return SIMDf_MUL(SIMDf_NUM(32), SIMDf_MASK_ADD(n0, SIMDf_MASK_ADD(n1, SIMDf_MASK_ADD(n2, v3, v2), v1), v0));
}

static SIMDf VECTORCALL FUNC(CubicSingle)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z)
{
	SIMDf xf1 = SIMDf_FLOOR(x);
	SIMDf yf1 = SIMDf_FLOOR(y);
	SIMDf zf1 = SIMDf_FLOOR(z);

	SIMDi x1 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(xf1), SIMDi_NUM(xPrime));
	SIMDi y1 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(yf1), SIMDi_NUM(yPrime));
	SIMDi z1 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(zf1), SIMDi_NUM(zPrime));

	SIMDi x0 = SIMDi_SUB(x1, SIMDi_NUM(xPrime));
	SIMDi y0 = SIMDi_SUB(y1, SIMDi_NUM(yPrime));
	SIMDi z0 = SIMDi_SUB(z1, SIMDi_NUM(zPrime));
	SIMDi x2 = SIMDi_ADD(x1, SIMDi_NUM(xPrime));
	SIMDi y2 = SIMDi_ADD(y1, SIMDi_NUM(yPrime));
	SIMDi z2 = SIMDi_ADD(z1, SIMDi_NUM(zPrime));
	SIMDi x3 = SIMDi_ADD(x2, SIMDi_NUM(xPrime));
	SIMDi y3 = SIMDi_ADD(y2, SIMDi_NUM(yPrime));
	SIMDi z3 = SIMDi_ADD(z2, SIMDi_NUM(zPrime));

	SIMDf xs = SIMDf_SUB(x, xf1);
	SIMDf ys = SIMDf_SUB(y, yf1);
	SIMDf zs = SIMDf_SUB(z, zf1);

	return SIMDf_MUL(FUNC(CubicLerp)(
		FUNC(CubicLerp)(
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y0, z0), FUNC(ValCoord)(seed, x1, y0, z0), FUNC(ValCoord)(seed, x2, y0, z0), FUNC(ValCoord)(seed, x3, y0, z0), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y1, z0), FUNC(ValCoord)(seed, x1, y1, z0), FUNC(ValCoord)(seed, x2, y1, z0), FUNC(ValCoord)(seed, x3, y1, z0), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y2, z0), FUNC(ValCoord)(seed, x1, y2, z0), FUNC(ValCoord)(seed, x2, y2, z0), FUNC(ValCoord)(seed, x3, y2, z0), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y3, z0), FUNC(ValCoord)(seed, x1, y3, z0), FUNC(ValCoord)(seed, x2, y3, z0), FUNC(ValCoord)(seed, x3, y3, z0), xs),
			ys),
		FUNC(CubicLerp)(
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y0, z1), FUNC(ValCoord)(seed, x1, y0, z1), FUNC(ValCoord)(seed, x2, y0, z1), FUNC(ValCoord)(seed, x3, y0, z1), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y1, z1), FUNC(ValCoord)(seed, x1, y1, z1), FUNC(ValCoord)(seed, x2, y1, z1), FUNC(ValCoord)(seed, x3, y1, z1), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y2, z1), FUNC(ValCoord)(seed, x1, y2, z1), FUNC(ValCoord)(seed, x2, y2, z1), FUNC(ValCoord)(seed, x3, y2, z1), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y3, z1), FUNC(ValCoord)(seed, x1, y3, z1), FUNC(ValCoord)(seed, x2, y3, z1), FUNC(ValCoord)(seed, x3, y3, z1), xs),
			ys),
		FUNC(CubicLerp)(
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y0, z2), FUNC(ValCoord)(seed, x1, y0, z2), FUNC(ValCoord)(seed, x2, y0, z2), FUNC(ValCoord)(seed, x3, y0, z2), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y1, z2), FUNC(ValCoord)(seed, x1, y1, z2), FUNC(ValCoord)(seed, x2, y1, z2), FUNC(ValCoord)(seed, x3, y1, z2), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y2, z2), FUNC(ValCoord)(seed, x1, y2, z2), FUNC(ValCoord)(seed, x2, y2, z2), FUNC(ValCoord)(seed, x3, y2, z2), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y3, z2), FUNC(ValCoord)(seed, x1, y3, z2), FUNC(ValCoord)(seed, x2, y3, z2), FUNC(ValCoord)(seed, x3, y3, z2), xs),
			ys),
		FUNC(CubicLerp)(
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y0, z3), FUNC(ValCoord)(seed, x1, y0, z3), FUNC(ValCoord)(seed, x2, y0, z3), FUNC(ValCoord)(seed, x3, y0, z3), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y1, z3), FUNC(ValCoord)(seed, x1, y1, z3), FUNC(ValCoord)(seed, x2, y1, z3), FUNC(ValCoord)(seed, x3, y1, z3), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y2, z3), FUNC(ValCoord)(seed, x1, y2, z3), FUNC(ValCoord)(seed, x2, y2, z3), FUNC(ValCoord)(seed, x3, y2, z3), xs),
			FUNC(CubicLerp)(FUNC(ValCoord)(seed, x0, y3, z3), FUNC(ValCoord)(seed, x1, y3, z3), FUNC(ValCoord)(seed, x2, y3, z3), FUNC(ValCoord)(seed, x3, y3, z3), xs),
			ys),
		zs), SIMDf_NUM(cubicBounding));
}

#define GRADIENT_COORD(_x,_y,_z)\
SIMDi hash##_x##_y##_z = FUNC(HashHB)(seed, x##_x, y##_y, z##_z); \
SIMDf x##_x##_y##_z = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(hash##_x##_y##_z, SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5)); \
SIMDf y##_x##_y##_z = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash##_x##_y##_z, 10), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5)); \
SIMDf z##_x##_y##_z = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash##_x##_y##_z, 20), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5)); 

//SIMDf invMag##_x##_y##_z = SIMDf_MUL(SIMDf_NUM(cellJitter), SIMDf_INV_SQRT(SIMDf_MUL_ADD(x##_x##_y##_z, x##_x##_y##_z, SIMDf_MUL_ADD(y##_x##_y##_z, y##_x##_y##_z, SIMDf_MUL(z##_x##_y##_z, z##_x##_y##_z)))));
//x##_x##_y##_z = SIMDf_MUL(x##_x##_y##_z, invMag##_x##_y##_z);
//y##_x##_y##_z = SIMDf_MUL(y##_x##_y##_z, invMag##_x##_y##_z); 
//z##_x##_y##_z = SIMDf_MUL(z##_x##_y##_z, invMag##_x##_y##_z);

static void VECTORCALL FUNC(GradientPerturbSingle)(SIMDi seed, SIMDf perturbAmp, SIMDf perturbFrequency, SIMDf& x, SIMDf& y, SIMDf& z)
{
	SIMDf xf = SIMDf_MUL(x, perturbFrequency);
	SIMDf yf = SIMDf_MUL(y, perturbFrequency);
	SIMDf zf = SIMDf_MUL(z, perturbFrequency);

	SIMDf xs = SIMDf_FLOOR(xf);
	SIMDf ys = SIMDf_FLOOR(yf);
	SIMDf zs = SIMDf_FLOOR(zf);

	SIMDi x0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(xs), SIMDi_NUM(xPrime));
	SIMDi y0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(ys), SIMDi_NUM(yPrime));
	SIMDi z0 = SIMDi_MUL(SIMDi_CONVERT_TO_INT(zs), SIMDi_NUM(zPrime));
	SIMDi x1 = SIMDi_ADD(x0, SIMDi_NUM(xPrime));
	SIMDi y1 = SIMDi_ADD(y0, SIMDi_NUM(yPrime));
	SIMDi z1 = SIMDi_ADD(z0, SIMDi_NUM(zPrime));

	xs = FUNC(InterpQuintic)(SIMDf_SUB(xf, xs));
	ys = FUNC(InterpQuintic)(SIMDf_SUB(yf, ys));
	zs = FUNC(InterpQuintic)(SIMDf_SUB(zf, zs));

	GRADIENT_COORD(0, 0, 0);
	GRADIENT_COORD(0, 0, 1);
	GRADIENT_COORD(0, 1, 0);
	GRADIENT_COORD(0, 1, 1);
	GRADIENT_COORD(1, 0, 0);
	GRADIENT_COORD(1, 0, 1);
	GRADIENT_COORD(1, 1, 0);
	GRADIENT_COORD(1, 1, 1);

	SIMDf x0y = FUNC(Lerp)(FUNC(Lerp)(x000, x100, xs), FUNC(Lerp)(x010, x110, xs), ys);
	SIMDf y0y = FUNC(Lerp)(FUNC(Lerp)(y000, y100, xs), FUNC(Lerp)(y010, y110, xs), ys);
	SIMDf z0y = FUNC(Lerp)(FUNC(Lerp)(z000, z100, xs), FUNC(Lerp)(z010, z110, xs), ys);

	SIMDf x1y = FUNC(Lerp)(FUNC(Lerp)(x001, x101, xs), FUNC(Lerp)(x011, x111, xs), ys);
	SIMDf y1y = FUNC(Lerp)(FUNC(Lerp)(y001, y101, xs), FUNC(Lerp)(y011, y111, xs), ys);
	SIMDf z1y = FUNC(Lerp)(FUNC(Lerp)(z001, z101, xs), FUNC(Lerp)(z011, z111, xs), ys);

	x = SIMDf_MUL_ADD(FUNC(Lerp)(x0y, x1y, zs), perturbAmp, x);
	y = SIMDf_MUL_ADD(FUNC(Lerp)(y0y, y1y, zs), perturbAmp, y);
	z = SIMDf_MUL_ADD(FUNC(Lerp)(z0y, z1y, zs), perturbAmp, z);
}

SIMD_LEVEL_CLASS::FASTNOISE_SIMD_CLASS(SIMD_LEVEL)(int seed)
{
	m_seed = seed;
	m_fractalBounding = CalculateFractalBounding(m_octaves, m_gain);
	m_perturbFractalBounding = CalculateFractalBounding(m_perturbOctaves, m_perturbGain);
	FUNC(InitSIMDValues)();
	s_currentSIMDLevel = SIMD_LEVEL;
}

int SIMD_LEVEL_CLASS::AlignedSize(int size)
{
#ifdef FN_ALIGNED_SETS
	// size must be a multiple of VECTOR_SIZE (8)
	if ((size & (VECTOR_SIZE - 1)) != 0)
	{
		size &= ~(VECTOR_SIZE - 1);
		size += VECTOR_SIZE;
	}
#endif
	return size;
}

float* SIMD_LEVEL_CLASS::GetEmptySet(int size)
{
	size = AlignedSize(size);

	float* noiseSet;
	SIMD_ALLOCATE_SET(noiseSet, size);

	return noiseSet;
}

#define AXIS_RESET(_zSize, _start) for (int _i = (_zSize) * (_start); _i < VECTOR_SIZE; _i+=(_zSize)){\
MASK _zReset = SIMDi_GREATER_THAN(z, zEndV);\
y = SIMDi_MASK_ADD(_zReset, y, SIMDi_NUM(1));\
z = SIMDi_MASK_SUB(_zReset, z, zSizeV);\
\
MASK _yReset = SIMDi_GREATER_THAN(y, yEndV);\
x = SIMDi_MASK_ADD(_yReset, x, SIMDi_NUM(1));\
y = SIMDi_MASK_SUB(_yReset, y, ySizeV);}

#ifdef FN_ALIGNED_SETS
#define STORE_LAST_RESULT(_dest, _source) SIMDf_STORE(_dest, _source)
#else
#include <cstring>
#define STORE_LAST_RESULT(_dest, _source) std::memcpy(_dest, &_source, (maxIndex - index) * 4)
#endif

#define INIT_PERTURB_VALUES() \
SIMDf perturbAmpV, perturbFreqV, perturbLacunarityV, perturbGainV, perturbNormaliseLengthV;\
switch (m_perturbType)\
{\
case None:\
	break;\
case Gradient_Normalise:\
	perturbNormaliseLengthV = SIMDf_SET(m_perturbNormaliseLength*m_frequency);\
case Gradient:\
	perturbAmpV = SIMDf_SET(m_perturbAmp);\
	perturbFreqV = SIMDf_SET(m_perturbFrequency);\
	break;\
case GradientFractal_Normalise:\
	perturbNormaliseLengthV = SIMDf_SET(m_perturbNormaliseLength*m_frequency);\
case GradientFractal:\
	perturbAmpV = SIMDf_SET(m_perturbAmp*m_fractalBounding);\
	perturbFreqV = SIMDf_SET(m_perturbFrequency);\
	perturbLacunarityV = SIMDf_SET(m_perturbLacunarity);\
	perturbGainV = SIMDf_SET(m_perturbGain);\
	break;\
case Normalise:\
	perturbNormaliseLengthV = SIMDf_SET(m_perturbNormaliseLength*m_frequency);\
	break;\
}

#define PERTURB_SWITCH()\
switch (m_perturbType)\
{\
case None:\
	break;\
case Gradient:\
	FUNC(GradientPerturbSingle)(SIMDi_SUB(seedV, SIMDi_NUM(1)), perturbAmpV, perturbFreqV, xF, yF, zF); \
	break; \
case GradientFractal:\
	{\
	SIMDi seedF = SIMDi_SUB(seedV, SIMDi_NUM(1));\
	SIMDf freqF = perturbFreqV;\
	SIMDf ampF = perturbAmpV;\
	\
	FUNC(GradientPerturbSingle)(seedF, ampF, freqF, xF, yF, zF);\
	\
	int octaveIndex = 0;\
	\
	while (++octaveIndex < m_perturbOctaves)\
	{\
		freqF = SIMDf_MUL(freqF, perturbLacunarityV);\
		seedF = SIMDi_SUB(seedF, SIMDi_NUM(1));\
		ampF = SIMDf_MUL(ampF, perturbGainV);\
		\
		FUNC(GradientPerturbSingle)(seedF, ampF, freqF, xF, yF, zF);\
	}}\
	break;\
case Gradient_Normalise:\
	FUNC(GradientPerturbSingle)(SIMDi_SUB(seedV, SIMDi_NUM(1)), perturbAmpV, perturbFreqV, xF, yF, zF); \
case Normalise:\
	{\
	SIMDf invMag = SIMDf_MUL(perturbNormaliseLengthV, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xF, xF, SIMDf_MUL_ADD(yF, yF, SIMDf_MUL(zF, zF)))));\
	xF = SIMDf_MUL(xF, invMag);\
	yF = SIMDf_MUL(yF, invMag);\
	zF = SIMDf_MUL(zF, invMag);\
	}break;\
case GradientFractal_Normalise:\
	{\
	SIMDi seedF = SIMDi_SUB(seedV, SIMDi_NUM(1));\
	SIMDf freqF = perturbFreqV;\
	SIMDf ampF = perturbAmpV;\
	\
	FUNC(GradientPerturbSingle)(seedF, ampF, freqF, xF, yF, zF);\
	\
	int octaveIndex = 0;\
	\
	while (++octaveIndex < m_perturbOctaves)\
	{\
		freqF = SIMDf_MUL(freqF, perturbLacunarityV);\
		seedF = SIMDi_SUB(seedF, SIMDi_NUM(1));\
		ampF = SIMDf_MUL(ampF, perturbGainV);\
		\
		FUNC(GradientPerturbSingle)(seedF, ampF, freqF, xF, yF, zF);\
	}\
	SIMDf invMag = SIMDf_MUL(perturbNormaliseLengthV, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xF, xF, SIMDf_MUL_ADD(yF, yF, SIMDf_MUL(zF, zF)))));\
	xF = SIMDf_MUL(xF, invMag);\
	yF = SIMDf_MUL(yF, invMag);\
	zF = SIMDf_MUL(zF, invMag);\
	}break;\
}

#define SET_BUILDER(f)\
if ((zSize & (VECTOR_SIZE - 1)) == 0)\
{\
	SIMDi yBase = SIMDi_SET(yStart);\
	SIMDi zBase = SIMDi_ADD(SIMDi_NUM(incremental), SIMDi_SET(zStart));\
	\
	SIMDi x = SIMDi_SET(xStart);\
	\
	int index = 0;\
	\
	for (int ix = 0; ix < xSize; ix++)\
	{\
		SIMDf xf = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(x), xFreqV);\
		SIMDi y = yBase;\
		\
		for (int iy = 0; iy < ySize; iy++)\
		{\
			SIMDf yf = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(y), yFreqV);\
			SIMDi z = zBase;\
			SIMDf xF = xf;\
			SIMDf yF = yf;\
			SIMDf zF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(z), zFreqV);\
			\
			PERTURB_SWITCH()\
			SIMDf result;\
			f;\
			SIMDf_STORE(&noiseSet[index], result);\
			\
			int iz = VECTOR_SIZE;\
			while (iz < zSize)\
			{\
				z = SIMDi_ADD(z, SIMDi_NUM(vectorSize));\
				index += VECTOR_SIZE;\
				iz += VECTOR_SIZE;\
				xF = xf;\
				yF = yf;\
				zF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(z), zFreqV);\
				\
				PERTURB_SWITCH()\
				SIMDf result;\
				f;\
				SIMDf_STORE(&noiseSet[index], result);\
			}\
			index += VECTOR_SIZE;\
			y = SIMDi_ADD(y, SIMDi_NUM(1));\
		}\
		x = SIMDi_ADD(x, SIMDi_NUM(1));\
	}\
}\
else\
{\
	SIMDi ySizeV = SIMDi_SET(ySize); \
	SIMDi zSizeV = SIMDi_SET(zSize); \
	\
	SIMDi yEndV = SIMDi_SET(yStart + ySize - 1); \
	SIMDi zEndV = SIMDi_SET(zStart + zSize - 1); \
	\
	SIMDi x = SIMDi_SET(xStart); \
	SIMDi y = SIMDi_SET(yStart); \
	SIMDi z = SIMDi_ADD(SIMDi_SET(zStart), SIMDi_NUM(incremental)); \
	AXIS_RESET(zSize, 1)\
	\
	int index = 0; \
	int maxIndex = xSize * ySize * zSize; \
	\
	for (; index < maxIndex - VECTOR_SIZE; index += VECTOR_SIZE)\
	{\
		SIMDf xF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(x), xFreqV);\
		SIMDf yF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(y), yFreqV);\
		SIMDf zF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(z), zFreqV);\
		\
		PERTURB_SWITCH()\
		SIMDf result;\
		f;\
		SIMDf_STORE(&noiseSet[index], result);\
		\
		z = SIMDi_ADD(z, SIMDi_NUM(vectorSize));\
		\
		AXIS_RESET(zSize, 0)\
	}\
	\
	SIMDf xF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(x), xFreqV);\
	SIMDf yF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(y), yFreqV);\
	SIMDf zF = SIMDf_MUL(SIMDf_CONVERT_TO_FLOAT(z), zFreqV);\
	\
	PERTURB_SWITCH()\
	SIMDf result;\
	f;\
	STORE_LAST_RESULT(&noiseSet[index], result);\
}

// FBM SINGLE
#define FBM_SINGLE(f)\
	SIMDi seedF = seedV;\
	\
	result = FUNC(f##Single)(seedF, xF, yF, zF);\
	\
	SIMDf ampF = SIMDf_NUM(1);\
	int octaveIndex = 0;\
	\
	while (++octaveIndex < m_octaves)\
	{\
		xF = SIMDf_MUL(xF, lacunarityV);\
		yF = SIMDf_MUL(yF, lacunarityV);\
		zF = SIMDf_MUL(zF, lacunarityV);\
		seedF = SIMDi_ADD(seedF, SIMDi_NUM(1));\
		\
		ampF = SIMDf_MUL(ampF, gainV);\
		result = SIMDf_MUL_ADD(FUNC(f##Single)(seedF, xF, yF, zF), ampF, result);\
	}\
	result = SIMDf_MUL(result, fractalBoundingV)

// BILLOW SINGLE
#define BILLOW_SINGLE(f)\
	SIMDi seedF = seedV;\
	\
	result = SIMDf_MUL_SUB(SIMDf_ABS(FUNC(f##Single)(seedF, xF, yF, zF)), SIMDf_NUM(2), SIMDf_NUM(1));\
	\
	SIMDf ampF = SIMDf_NUM(1);\
	int octaveIndex = 0;\
	\
	while (++octaveIndex < m_octaves)\
	{\
		xF = SIMDf_MUL(xF, lacunarityV);\
		yF = SIMDf_MUL(yF, lacunarityV);\
		zF = SIMDf_MUL(zF, lacunarityV);\
		seedF = SIMDi_ADD(seedF, SIMDi_NUM(1));\
		\
		ampF = SIMDf_MUL(ampF, gainV);\
		result = SIMDf_MUL_ADD(SIMDf_MUL_SUB(SIMDf_ABS(FUNC(f##Single)(seedF, xF, yF, zF)), SIMDf_NUM(2), SIMDf_NUM(1)), ampF, result);\
	}\
	result = SIMDf_MUL(result, fractalBoundingV)

// RIGIDMULTI SINGLE
#define RIGIDMULTI_SINGLE(f)\
	SIMDi seedF = seedV;\
	\
	result = SIMDf_SUB(SIMDf_NUM(1), SIMDf_ABS(FUNC(f##Single)(seedF, xF, yF, zF)));\
	\
	SIMDf ampF = SIMDf_NUM(1);\
	int octaveIndex = 0;\
	\
	while (++octaveIndex < m_octaves)\
	{\
		xF = SIMDf_MUL(xF, lacunarityV);\
		yF = SIMDf_MUL(yF, lacunarityV);\
		zF = SIMDf_MUL(zF, lacunarityV);\
		seedF = SIMDi_ADD(seedF, SIMDi_NUM(1));\
		\
		ampF = SIMDf_MUL(ampF, gainV);\
		result = SIMDf_NMUL_ADD(SIMDf_SUB(SIMDf_NUM(1), SIMDf_ABS(FUNC(f##Single)(seedF, xF, yF, zF))), ampF, result);\
	}

#define FILL_SET(func) \
void SIMD_LEVEL_CLASS::Fill##func##Set(float* noiseSet, int xStart, int yStart, int zStart, int xSize, int ySize, int zSize, float scaleModifier)\
{\
	assert(noiseSet);\
	SIMD_ZERO_ALL();\
	SIMDi seedV = SIMDi_SET(m_seed); \
	INIT_PERTURB_VALUES();\
	\
	scaleModifier *= m_frequency;\
	\
	SIMDf xFreqV = SIMDf_SET(scaleModifier * m_xScale);\
	SIMDf yFreqV = SIMDf_SET(scaleModifier * m_yScale);\
	SIMDf zFreqV = SIMDf_SET(scaleModifier * m_zScale);\
	\
	SET_BUILDER(result = FUNC(func##Single)(seedV, xF, yF, zF))\
	\
	SIMD_ZERO_ALL();\
}

#define FILL_FRACTAL_SET(func) \
void SIMD_LEVEL_CLASS::Fill##func##FractalSet(float* noiseSet, int xStart, int yStart, int zStart, int xSize, int ySize, int zSize, float scaleModifier)\
{\
	assert(noiseSet);\
	SIMD_ZERO_ALL();\
	\
	SIMDi seedV = SIMDi_SET(m_seed);\
	SIMDf lacunarityV = SIMDf_SET(m_lacunarity);\
	SIMDf gainV = SIMDf_SET(m_gain);\
	SIMDf fractalBoundingV = SIMDf_SET(m_fractalBounding);\
	INIT_PERTURB_VALUES();\
	\
	scaleModifier *= m_frequency;\
	\
	SIMDf xFreqV = SIMDf_SET(scaleModifier * m_xScale);\
	SIMDf yFreqV = SIMDf_SET(scaleModifier * m_yScale);\
	SIMDf zFreqV = SIMDf_SET(scaleModifier * m_zScale);\
	\
	switch(m_fractalType)\
	{\
	case FBM:\
		SET_BUILDER(FBM_SINGLE(func))\
		break;\
	case Billow:\
		SET_BUILDER(BILLOW_SINGLE(func))\
		break;\
	case RigidMulti:\
		SET_BUILDER(RIGIDMULTI_SINGLE(func))\
		break;\
	}\
	SIMD_ZERO_ALL();\
}

FILL_SET(Value)
FILL_FRACTAL_SET(Value)

FILL_SET(Perlin)
FILL_FRACTAL_SET(Perlin)

FILL_SET(Simplex)
FILL_FRACTAL_SET(Simplex)

//FILL_SET(WhiteNoise)

FILL_SET(Cubic)
FILL_FRACTAL_SET(Cubic)

#ifdef FN_ALIGNED_SETS
#define SIZE_MASK
#define SAFE_LAST(f)
#else
#define SIZE_MASK & ~(VECTOR_SIZE - 1)
#define SAFE_LAST(f)\
if (loopMax != vectorSet->size)\
{\
	std::size_t remaining = (vectorSet->size - loopMax) * 4;\
	\
	SIMDf xF = SIMDf_LOAD(&vectorSet->xSet[loopMax]);\
	SIMDf yF = SIMDf_LOAD(&vectorSet->ySet[loopMax]);\
	SIMDf zF = SIMDf_LOAD(&vectorSet->zSet[loopMax]);\
	\
	xF = SIMDf_MUL_ADD(xF, xFreqV, xOffsetV);\
	yF = SIMDf_MUL_ADD(yF, yFreqV, yOffsetV);\
	zF = SIMDf_MUL_ADD(zF, zFreqV, zOffsetV);\
	\
	SIMDf result;\
	f;\
	std::memcpy(&noiseSet[index], &result, remaining);\
}
#endif

#define VECTOR_SET_BUILDER(f)\
while (index < loopMax)\
{\
	SIMDf xF = SIMDf_MUL_ADD(SIMDf_LOAD(&vectorSet->xSet[index]), xFreqV, xOffsetV);\
	SIMDf yF = SIMDf_MUL_ADD(SIMDf_LOAD(&vectorSet->ySet[index]), yFreqV, yOffsetV);\
	SIMDf zF = SIMDf_MUL_ADD(SIMDf_LOAD(&vectorSet->zSet[index]), zFreqV, zOffsetV);\
	\
	PERTURB_SWITCH()\
	SIMDf result;\
	f;\
	SIMDf_STORE(&noiseSet[index], result);\
	index += VECTOR_SIZE;\
}\
SAFE_LAST(f)

#define FILL_VECTOR_SET(func)\
void SIMD_LEVEL_CLASS::Fill##func##Set(float* noiseSet, FastNoiseVectorSet* vectorSet, float xOffset, float yOffset, float zOffset)\
{\
	assert(noiseSet);\
	assert(vectorSet);\
	assert(vectorSet->size >= 0);\
	SIMD_ZERO_ALL();\
	\
	SIMDi seedV = SIMDi_SET(m_seed);\
	SIMDf xFreqV = SIMDf_SET(m_frequency * m_xScale);\
	SIMDf yFreqV = SIMDf_SET(m_frequency * m_yScale);\
	SIMDf zFreqV = SIMDf_SET(m_frequency * m_zScale);\
	SIMDf xOffsetV = SIMDf_MUL(SIMDf_SET(xOffset), xFreqV);\
	SIMDf yOffsetV = SIMDf_MUL(SIMDf_SET(yOffset), yFreqV);\
	SIMDf zOffsetV = SIMDf_MUL(SIMDf_SET(zOffset), zFreqV);\
	INIT_PERTURB_VALUES();\
	\
	int index = 0;\
	int loopMax = vectorSet->size SIZE_MASK;\
	\
	VECTOR_SET_BUILDER(result = FUNC(func##Single)(seedV, xF, yF, zF))\
	SIMD_ZERO_ALL();\
}

#define FILL_FRACTAL_VECTOR_SET(func)\
void SIMD_LEVEL_CLASS::Fill##func##FractalSet(float* noiseSet, FastNoiseVectorSet* vectorSet, float xOffset, float yOffset, float zOffset)\
{\
	assert(noiseSet);\
	assert(vectorSet);\
	assert(vectorSet->size >= 0);\
	SIMD_ZERO_ALL();\
	\
	SIMDi seedV = SIMDi_SET(m_seed);\
	SIMDf lacunarityV = SIMDf_SET(m_lacunarity);\
	SIMDf gainV = SIMDf_SET(m_gain);\
	SIMDf fractalBoundingV = SIMDf_SET(m_fractalBounding);\
	SIMDf xFreqV = SIMDf_SET(m_frequency * m_xScale);\
	SIMDf yFreqV = SIMDf_SET(m_frequency * m_yScale);\
	SIMDf zFreqV = SIMDf_SET(m_frequency * m_zScale);\
	SIMDf xOffsetV = SIMDf_MUL(SIMDf_SET(xOffset), xFreqV);\
	SIMDf yOffsetV = SIMDf_MUL(SIMDf_SET(yOffset), yFreqV);\
	SIMDf zOffsetV = SIMDf_MUL(SIMDf_SET(zOffset), zFreqV);\
	INIT_PERTURB_VALUES();\
	\
	int index = 0;\
	int loopMax = vectorSet->size SIZE_MASK;\
	\
	switch(m_fractalType)\
	{\
	case FBM:\
		VECTOR_SET_BUILDER(FBM_SINGLE(func))\
		break;\
	case Billow:\
		VECTOR_SET_BUILDER(BILLOW_SINGLE(func))\
		break;\
	case RigidMulti:\
		VECTOR_SET_BUILDER(RIGIDMULTI_SINGLE(func))\
		break;\
	}\
	SIMD_ZERO_ALL();\
}

	FILL_VECTOR_SET(Value)
	FILL_FRACTAL_VECTOR_SET(Value)

	FILL_VECTOR_SET(Perlin)
	FILL_FRACTAL_VECTOR_SET(Perlin)

	FILL_VECTOR_SET(Simplex)
	FILL_FRACTAL_VECTOR_SET(Simplex)

	FILL_VECTOR_SET(WhiteNoise)

	FILL_VECTOR_SET(Cubic)
	FILL_FRACTAL_VECTOR_SET(Cubic)

	void SIMD_LEVEL_CLASS::FillWhiteNoiseSet(float* noiseSet, int xStart, int yStart, int zStart, int xSize, int ySize, int zSize, float scaleModifier)
{
	assert(noiseSet);
	SIMD_ZERO_ALL();
	SIMDi seedV = SIMDi_SET(m_seed);

	if ((zSize & (VECTOR_SIZE - 1)) == 0)
	{
		SIMDi x = SIMDi_MUL(SIMDi_SET(xStart), SIMDi_NUM(xPrime));
		SIMDi yBase = SIMDi_MUL(SIMDi_SET(yStart), SIMDi_NUM(yPrime));
		SIMDi zBase = SIMDi_MUL(SIMDi_ADD(SIMDi_NUM(incremental), SIMDi_SET(zStart)), SIMDi_NUM(zPrime));

		SIMDi zStep = SIMDi_MUL(SIMDi_NUM(vectorSize), SIMDi_NUM(zPrime));

		int index = 0;

		for (int ix = 0; ix < xSize; ix++)
		{
			SIMDi y = yBase;

			for (int iy = 0; iy < ySize; iy++)
			{
				SIMDi z = zBase;

				SIMDf_STORE(&noiseSet[index], FUNC(ValCoord)(seedV, x, y, z));

				int iz = VECTOR_SIZE;
				while (iz < zSize)
				{
					z = SIMDi_ADD(z, zStep);
					index += VECTOR_SIZE;
					iz += VECTOR_SIZE;

					SIMDf_STORE(&noiseSet[index], FUNC(ValCoord)(seedV, x, y, z));
				}
				index += VECTOR_SIZE;
				y = SIMDi_ADD(y, SIMDi_NUM(yPrime));
			}
			x = SIMDi_ADD(x, SIMDi_NUM(xPrime));
		}
	}
	else
	{
		SIMDi ySizeV = SIMDi_SET(ySize);
		SIMDi zSizeV = SIMDi_SET(zSize);

		SIMDi yEndV = SIMDi_SET(yStart + ySize - 1);
		SIMDi zEndV = SIMDi_SET(zStart + zSize - 1);

		SIMDi x = SIMDi_SET(xStart);
		SIMDi y = SIMDi_SET(yStart);
		SIMDi z = SIMDi_ADD(SIMDi_SET(zStart), SIMDi_NUM(incremental));
		AXIS_RESET(zSize, 1);

		int index = 0;
		int maxIndex = xSize * ySize * zSize;

		for (; index < maxIndex - VECTOR_SIZE; index += VECTOR_SIZE)
		{
			SIMDf_STORE(&noiseSet[index], FUNC(ValCoord)(seedV, SIMDi_MUL(x, SIMDi_NUM(xPrime)), SIMDi_MUL(y, SIMDi_NUM(yPrime)), SIMDi_MUL(z, SIMDi_NUM(zPrime))));

			z = SIMDi_ADD(z, SIMDi_NUM(vectorSize));

			AXIS_RESET(zSize, 0);
		}
		SIMDf result = FUNC(ValCoord)(seedV, SIMDi_MUL(x, SIMDi_NUM(xPrime)), SIMDi_MUL(y, SIMDi_NUM(yPrime)), SIMDi_MUL(z, SIMDi_NUM(zPrime)));
		STORE_LAST_RESULT(&noiseSet[index], result);
	}
	SIMD_ZERO_ALL();
}

#define Euclidean_DISTANCE(_x, _y, _z) SIMDf_MUL_ADD(_x, _x, SIMDf_MUL_ADD(_y, _y, SIMDf_MUL(_z, _z)))
#define Manhattan_DISTANCE(_x, _y, _z) SIMDf_ADD(SIMDf_ADD(SIMDf_ABS(_x), SIMDf_ABS(_y)), SIMDf_ABS(_z))
#define Natural_DISTANCE(_x, _y, _z) SIMDf_ADD(Euclidean_DISTANCE(_x,_y,_z), Manhattan_DISTANCE(_x,_y,_z))

#define Distance2_RETURN(_distance, _distance2) (_distance2)
#define Distance2Add_RETURN(_distance, _distance2) SIMDf_ADD(_distance, _distance2)
#define Distance2Sub_RETURN(_distance, _distance2) SIMDf_SUB(_distance2, _distance)
#define Distance2Mul_RETURN(_distance, _distance2) SIMDf_MUL(_distance, _distance2)
#define Distance2Div_RETURN(_distance, _distance2) SIMDf_DIV(_distance, _distance2)

#define CELLULAR_VALUE_SINGLE(distanceFunc)\
static SIMDf VECTORCALL FUNC(CellularValue##distanceFunc##Single)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z, SIMDf cellJitter)\
{\
	SIMDf distance = SIMDf_NUM(999999);\
	SIMDf cellValue = SIMDf_UNDEFINED();\
	\
	SIMDi xc     = SIMDi_SUB(SIMDi_CONVERT_TO_INT(x), SIMDi_NUM(1));\
	SIMDi ycBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(y), SIMDi_NUM(1));\
	SIMDi zcBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(z), SIMDi_NUM(1));\
	\
	SIMDf xcf     = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(xc), x);\
	SIMDf ycfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(ycBase), y);\
	SIMDf zcfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(zcBase), z);\
	\
	xc     = SIMDi_MUL(xc, SIMDi_NUM(xPrime));\
	ycBase = SIMDi_MUL(ycBase, SIMDi_NUM(yPrime));\
	zcBase = SIMDi_MUL(zcBase, SIMDi_NUM(zPrime));\
	\
	for (int xi = 0; xi < 3; xi++)\
	{\
		SIMDf ycf = ycfBase;\
		SIMDi yc = ycBase;\
		for (int yi = 0; yi < 3; yi++)\
		{\
			SIMDf zcf = zcfBase;\
			SIMDi zc = zcBase;\
			for (int zi = 0; zi < 3; zi++)\
			{\
				SIMDi hash = FUNC(HashHB)(seed, xc, yc, zc);\
				SIMDf xd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(hash, SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf yd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,10), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf zd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,20), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				\
				SIMDf invMag = SIMDf_MUL(cellJitter, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xd, xd, SIMDf_MUL_ADD(yd, yd, SIMDf_MUL(zd, zd)))));\
				\
				xd = SIMDf_MUL_ADD(xd, invMag, xcf);\
				yd = SIMDf_MUL_ADD(yd, invMag, ycf);\
				zd = SIMDf_MUL_ADD(zd, invMag, zcf);\
				\
				SIMDf newCellValue = SIMDf_MUL(SIMDf_NUM(hash2Float), SIMDf_CONVERT_TO_FLOAT(hash));\
				SIMDf newDistance = distanceFunc##_DISTANCE(xd, yd, zd);\
				\
				MASK closer = SIMDf_LESS_THAN(newDistance, distance);\
				\
				distance = SIMDf_MIN(newDistance, distance);\
				cellValue = SIMDf_BLENDV(cellValue, newCellValue, closer);\
				\
				zcf = SIMDf_ADD(zcf, SIMDf_NUM(1));\
				zc = SIMDi_ADD(zc, SIMDi_NUM(zPrime));\
			}\
			ycf = SIMDf_ADD(ycf, SIMDf_NUM(1));\
			yc = SIMDi_ADD(yc, SIMDi_NUM(yPrime));\
		}\
		xcf = SIMDf_ADD(xcf, SIMDf_NUM(1));\
		xc = SIMDi_ADD(xc, SIMDi_NUM(xPrime));\
	}\
	\
	return cellValue;\
}

struct NoiseLookupSettings
{
	FastNoiseSIMD::NoiseType type;
	SIMDf frequency;
	FastNoiseSIMD::FractalType fractalType;
	int fractalOctaves;
	SIMDf fractalLacunarity;
	SIMDf fractalGain;
	SIMDf fractalBounding;
};

#define CELLULAR_LOOKUP_FRACTAL_VALUE(noiseType){\
SIMDf lacunarityV = noiseLookupSettings.fractalLacunarity;\
SIMDf gainV = noiseLookupSettings.fractalGain;\
SIMDf fractalBoundingV = noiseLookupSettings.fractalBounding;\
int m_octaves = noiseLookupSettings.fractalOctaves;\
switch(noiseLookupSettings.fractalType)\
{\
	case FastNoiseSIMD::FBM:\
		{FBM_SINGLE(noiseType);}\
		break;\
	case FastNoiseSIMD::Billow:\
		{BILLOW_SINGLE(noiseType);}\
		break;\
	case FastNoiseSIMD::RigidMulti:\
		{RIGIDMULTI_SINGLE(noiseType);}\
		break;\
}}\

#define CELLULAR_LOOKUP_SINGLE(distanceFunc)\
static SIMDf VECTORCALL FUNC(CellularLookup##distanceFunc##Single)(SIMDi seedV, SIMDf x, SIMDf y, SIMDf z, SIMDf cellJitter, const NoiseLookupSettings& noiseLookupSettings)\
{\
	SIMDf distance = SIMDf_NUM(999999);\
	SIMDf xCell = SIMDf_UNDEFINED();\
	SIMDf yCell = SIMDf_UNDEFINED();\
	SIMDf zCell = SIMDf_UNDEFINED();\
	\
	SIMDi xc     = SIMDi_SUB(SIMDi_CONVERT_TO_INT(x), SIMDi_NUM(1));\
	SIMDi ycBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(y), SIMDi_NUM(1));\
	SIMDi zcBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(z), SIMDi_NUM(1));\
	\
	SIMDf xcf     = SIMDf_CONVERT_TO_FLOAT(xc);\
	SIMDf ycfBase = SIMDf_CONVERT_TO_FLOAT(ycBase);\
	SIMDf zcfBase = SIMDf_CONVERT_TO_FLOAT(zcBase);\
	\
	xc     = SIMDi_MUL(xc, SIMDi_NUM(xPrime));\
	ycBase = SIMDi_MUL(ycBase, SIMDi_NUM(yPrime));\
	zcBase = SIMDi_MUL(zcBase, SIMDi_NUM(zPrime));\
	\
	for (int xi = 0; xi < 3; xi++)\
	{\
		SIMDf ycf = ycfBase;\
		SIMDi yc = ycBase;\
		SIMDf xLocal = SIMDf_SUB(xcf, x);\
		for (int yi = 0; yi < 3; yi++)\
		{\
			SIMDf zcf = zcfBase;\
			SIMDi zc = zcBase;\
			SIMDf yLocal = SIMDf_SUB(ycf, y);\
			for (int zi = 0; zi < 3; zi++)\
			{\
				SIMDf zLocal = SIMDf_SUB(zcf, z);\
				\
				SIMDi hash = FUNC(HashHB)(seedV, xc, yc, zc);\
				SIMDf xd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(hash, SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf yd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,10), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf zd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,20), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				\
				SIMDf invMag = SIMDf_MUL(cellJitter, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xd, xd, SIMDf_MUL_ADD(yd, yd, SIMDf_MUL(zd, zd)))));\
				\
				SIMDf xCellNew = SIMDf_MUL(xd, invMag);\
				SIMDf yCellNew = SIMDf_MUL(yd, invMag);\
				SIMDf zCellNew = SIMDf_MUL(zd, invMag);\
				\
				xd = SIMDf_ADD(xCellNew, xLocal);\
				yd = SIMDf_ADD(yCellNew, yLocal);\
				zd = SIMDf_ADD(zCellNew, zLocal);\
				\
				xCellNew = SIMDf_ADD(xCellNew, xcf); \
				yCellNew = SIMDf_ADD(yCellNew, ycf); \
				zCellNew = SIMDf_ADD(zCellNew, zcf); \
				\
				SIMDf newDistance = distanceFunc##_DISTANCE(xd, yd, zd);\
				\
				MASK closer = SIMDf_LESS_THAN(newDistance, distance);\
				\
				distance = SIMDf_MIN(newDistance, distance);\
				xCell = SIMDf_BLENDV(xCell, xCellNew, closer);\
				yCell = SIMDf_BLENDV(yCell, yCellNew, closer);\
				zCell = SIMDf_BLENDV(zCell, zCellNew, closer);\
				\
				zcf = SIMDf_ADD(zcf, SIMDf_NUM(1));\
				zc = SIMDi_ADD(zc, SIMDi_NUM(zPrime));\
			}\
			ycf = SIMDf_ADD(ycf, SIMDf_NUM(1));\
			yc = SIMDi_ADD(yc, SIMDi_NUM(yPrime));\
		}\
		xcf = SIMDf_ADD(xcf, SIMDf_NUM(1));\
		xc = SIMDi_ADD(xc, SIMDi_NUM(xPrime));\
	}\
	\
	SIMDf xF = SIMDf_MUL(xCell, noiseLookupSettings.frequency);\
	SIMDf yF = SIMDf_MUL(yCell, noiseLookupSettings.frequency);\
	SIMDf zF = SIMDf_MUL(zCell, noiseLookupSettings.frequency);\
	SIMDf result;\
	\
	switch(noiseLookupSettings.type)\
	{\
	default:\
		break;\
	case FastNoiseSIMD::Value:\
		result = FUNC(ValueSingle)(seedV, xF, yF, zF); \
		break;\
	case FastNoiseSIMD::ValueFractal:\
		CELLULAR_LOOKUP_FRACTAL_VALUE(Value);\
		break; \
	case FastNoiseSIMD::Perlin:\
		result = FUNC(PerlinSingle)(seedV, xF, yF, zF); \
		break;\
	case FastNoiseSIMD::PerlinFractal:\
		CELLULAR_LOOKUP_FRACTAL_VALUE(Perlin);\
		break; \
	case FastNoiseSIMD::Simplex:\
		result = FUNC(SimplexSingle)(seedV, xF, yF, zF); \
		break;\
	case FastNoiseSIMD::SimplexFractal:\
		CELLULAR_LOOKUP_FRACTAL_VALUE(Simplex);\
		break; \
	case FastNoiseSIMD::Cubic:\
		result = FUNC(CubicSingle)(seedV, xF, yF, zF); \
		break;\
	case FastNoiseSIMD::CubicFractal:\
		CELLULAR_LOOKUP_FRACTAL_VALUE(Cubic);\
		break; \
	}\
	\
	return result;\
}

#define CELLULAR_DISTANCE_SINGLE(distanceFunc)\
static SIMDf VECTORCALL FUNC(CellularDistance##distanceFunc##Single)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z, SIMDf cellJitter)\
{\
	SIMDf distance = SIMDf_NUM(999999);\
	\
	SIMDi xc     = SIMDi_SUB(SIMDi_CONVERT_TO_INT(x), SIMDi_NUM(1));\
	SIMDi ycBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(y), SIMDi_NUM(1));\
	SIMDi zcBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(z), SIMDi_NUM(1));\
	\
	SIMDf xcf     = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(xc), x);\
	SIMDf ycfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(ycBase), y);\
	SIMDf zcfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(zcBase), z);\
	\
	xc     = SIMDi_MUL(xc, SIMDi_NUM(xPrime));\
	ycBase = SIMDi_MUL(ycBase, SIMDi_NUM(yPrime));\
	zcBase = SIMDi_MUL(zcBase, SIMDi_NUM(zPrime));\
	\
	for (int xi = 0; xi < 3; xi++)\
	{\
		SIMDf ycf = ycfBase;\
		SIMDi yc = ycBase;\
		for (int yi = 0; yi < 3; yi++)\
		{\
			SIMDf zcf = zcfBase;\
			SIMDi zc = zcBase;\
			for (int zi = 0; zi < 3; zi++)\
			{\
				SIMDi hash = FUNC(HashHB)(seed, xc, yc, zc);\
				SIMDf xd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(hash, SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf yd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,10), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf zd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,20), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				\
				SIMDf invMag = SIMDf_MUL(cellJitter, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xd, xd, SIMDf_MUL_ADD(yd, yd, SIMDf_MUL(zd, zd)))));\
				\
				xd = SIMDf_MUL_ADD(xd, invMag, xcf);\
				yd = SIMDf_MUL_ADD(yd, invMag, ycf);\
				zd = SIMDf_MUL_ADD(zd, invMag, zcf);\
				\
				SIMDf newDistance = distanceFunc##_DISTANCE(xd, yd, zd);\
				\
				distance = SIMDf_MIN(distance, newDistance);\
				\
				zcf = SIMDf_ADD(zcf, SIMDf_NUM(1));\
				zc = SIMDi_ADD(zc, SIMDi_NUM(zPrime));\
			}\
			ycf = SIMDf_ADD(ycf, SIMDf_NUM(1));\
			yc = SIMDi_ADD(yc, SIMDi_NUM(yPrime));\
		}\
		xcf = SIMDf_ADD(xcf, SIMDf_NUM(1));\
		xc = SIMDi_ADD(xc, SIMDi_NUM(xPrime));\
	}\
	\
	return distance;\
}

#define CELLULAR_DISTANCE2_SINGLE(distanceFunc, returnFunc)\
static SIMDf VECTORCALL FUNC(Cellular##returnFunc##distanceFunc##Single)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z, SIMDf cellJitter, int index0, int index1)\
{\
	SIMDf distance[4] = {SIMDf_NUM(999999),SIMDf_NUM(999999),SIMDf_NUM(999999),SIMDf_NUM(999999)};\
	\
	SIMDi xc     = SIMDi_SUB(SIMDi_CONVERT_TO_INT(x), SIMDi_NUM(1));\
	SIMDi ycBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(y), SIMDi_NUM(1));\
	SIMDi zcBase = SIMDi_SUB(SIMDi_CONVERT_TO_INT(z), SIMDi_NUM(1));\
	\
	SIMDf xcf     = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(xc), x);\
	SIMDf ycfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(ycBase), y);\
	SIMDf zcfBase = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(zcBase), z);\
	\
	xc     = SIMDi_MUL(xc, SIMDi_NUM(xPrime));\
	ycBase = SIMDi_MUL(ycBase, SIMDi_NUM(yPrime));\
	zcBase = SIMDi_MUL(zcBase, SIMDi_NUM(zPrime));\
	\
	for (int xi = 0; xi < 3; xi++)\
	{\
		SIMDf ycf = ycfBase;\
		SIMDi yc = ycBase;\
		for (int yi = 0; yi < 3; yi++)\
		{\
			SIMDf zcf = zcfBase;\
			SIMDi zc = zcBase;\
			for (int zi = 0; zi < 3; zi++)\
			{\
				SIMDi hash = FUNC(HashHB)(seed, xc, yc, zc);\
				SIMDf xd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(hash, SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf yd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,10), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				SIMDf zd = SIMDf_SUB(SIMDf_CONVERT_TO_FLOAT(SIMDi_AND(SIMDi_SHIFT_R(hash,20), SIMDi_NUM(bit10Mask))), SIMDf_NUM(511_5));\
				\
				SIMDf invMag = SIMDf_MUL(cellJitter, SIMDf_INV_SQRT(SIMDf_MUL_ADD(xd, xd, SIMDf_MUL_ADD(yd, yd, SIMDf_MUL(zd, zd)))));\
				\
				xd = SIMDf_MUL_ADD(xd, invMag, xcf);\
				yd = SIMDf_MUL_ADD(yd, invMag, ycf);\
				zd = SIMDf_MUL_ADD(zd, invMag, zcf);\
				\
				SIMDf newDistance = distanceFunc##_DISTANCE(xd, yd, zd);\
				\
				for(int i = index1; i > 0; i--)\
					distance[i] = SIMDf_MAX(SIMDf_MIN(distance[i], newDistance), distance[i-1]);\
				distance[0] = SIMDf_MIN(distance[0], newDistance);\
				\
				zcf = SIMDf_ADD(zcf, SIMDf_NUM(1));\
				zc = SIMDi_ADD(zc, SIMDi_NUM(zPrime));\
			}\
			ycf = SIMDf_ADD(ycf, SIMDf_NUM(1));\
			yc = SIMDi_ADD(yc, SIMDi_NUM(yPrime));\
		}\
		xcf = SIMDf_ADD(xcf, SIMDf_NUM(1));\
		xc = SIMDi_ADD(xc, SIMDi_NUM(xPrime));\
	}\
	\
	return returnFunc##_RETURN(distance[index0], distance[index1]);\
}

#define CELLULAR_DISTANCE2CAVE_SINGLE(distanceFunc)\
static SIMDf VECTORCALL FUNC(CellularDistance2Cave##distanceFunc##Single)(SIMDi seed, SIMDf x, SIMDf y, SIMDf z, SIMDf cellJitter, int index0, int index1)\
{\
	SIMDf c0 = FUNC(CellularDistance2Div##distanceFunc##Single)(seed, x, y, z, cellJitter, index0, index1);\
	\
	x = SIMDf_ADD(x, SIMDf_NUM(0_5));\
	y = SIMDf_ADD(y, SIMDf_NUM(0_5));\
	z = SIMDf_ADD(z, SIMDf_NUM(0_5));\
	seed = SIMDi_ADD(seed, SIMDi_NUM(1));\
	\
	SIMDf c1 = FUNC(CellularDistance2Div##distanceFunc##Single)(seed, x, y, z, cellJitter, index0, index1);\
	\
	return SIMDf_MIN(c0,c1);\
}

CELLULAR_VALUE_SINGLE(Euclidean)
CELLULAR_VALUE_SINGLE(Manhattan)
CELLULAR_VALUE_SINGLE(Natural)

CELLULAR_LOOKUP_SINGLE(Euclidean)
CELLULAR_LOOKUP_SINGLE(Manhattan)
CELLULAR_LOOKUP_SINGLE(Natural)

#undef Natural_DISTANCE
#define Natural_DISTANCE(_x, _y, _z) SIMDf_MUL(Euclidean_DISTANCE(_x,_y,_z), Manhattan_DISTANCE(_x,_y,_z))

CELLULAR_DISTANCE_SINGLE(Euclidean)
CELLULAR_DISTANCE_SINGLE(Manhattan)
CELLULAR_DISTANCE_SINGLE(Natural)

#define CELLULAR_DISTANCE2_MULTI(returnFunc)\
CELLULAR_DISTANCE2_SINGLE(Euclidean, returnFunc)\
CELLULAR_DISTANCE2_SINGLE(Manhattan, returnFunc)\
CELLULAR_DISTANCE2_SINGLE(Natural, returnFunc)

CELLULAR_DISTANCE2_MULTI(Distance2)
CELLULAR_DISTANCE2_MULTI(Distance2Add)
CELLULAR_DISTANCE2_MULTI(Distance2Sub)
CELLULAR_DISTANCE2_MULTI(Distance2Div)
CELLULAR_DISTANCE2_MULTI(Distance2Mul)

CELLULAR_DISTANCE2CAVE_SINGLE(Euclidean)
CELLULAR_DISTANCE2CAVE_SINGLE(Manhattan)
CELLULAR_DISTANCE2CAVE_SINGLE(Natural)

#define CELLULAR_MULTI(returnFunc)\
switch(m_cellularDistanceFunction)\
{\
case Euclidean:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##EuclideanSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
case Manhattan:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##ManhattanSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
case Natural:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##NaturalSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
}

#define CELLULAR_INDEX_MULTI(returnFunc)\
switch(m_cellularDistanceFunction)\
{\
case Euclidean:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##EuclideanSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
case Manhattan:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##ManhattanSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
case Natural:\
	SET_BUILDER(result = FUNC(Cellular##returnFunc##NaturalSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
}

void SIMD_LEVEL_CLASS::FillCellularSet(float* noiseSet, int xStart, int yStart, int zStart, int xSize, int ySize, int zSize, float scaleModifier)
{
	assert(noiseSet);
	SIMD_ZERO_ALL();
	SIMDi seedV = SIMDi_SET(m_seed);
	INIT_PERTURB_VALUES();

	scaleModifier *= m_frequency;

	SIMDf xFreqV = SIMDf_SET(scaleModifier * m_xScale);
	SIMDf yFreqV = SIMDf_SET(scaleModifier * m_yScale);
	SIMDf zFreqV = SIMDf_SET(scaleModifier * m_zScale);
	SIMDf cellJitterV = SIMDf_SET(m_cellularJitter);

	NoiseLookupSettings nls;

	switch (m_cellularReturnType)
	{
	case CellValue:
		CELLULAR_MULTI(Value);
		break;
	case Distance:
		CELLULAR_MULTI(Distance);
		break;
	case Distance2:
		CELLULAR_INDEX_MULTI(Distance2);
		break;
	case Distance2Add:
		CELLULAR_INDEX_MULTI(Distance2Add);
		break;
	case Distance2Sub:
		CELLULAR_INDEX_MULTI(Distance2Sub);
		break;
	case Distance2Mul:
		CELLULAR_INDEX_MULTI(Distance2Mul);
		break;
	case Distance2Div:
		CELLULAR_INDEX_MULTI(Distance2Div);
		break;
	case Distance2Cave:
		CELLULAR_INDEX_MULTI(Distance2Cave);
		break;
	case NoiseLookup:
		nls.type = m_cellularNoiseLookupType;
		nls.frequency = SIMDf_SET(m_cellularNoiseLookupFrequency);
		nls.fractalType = m_fractalType;
		nls.fractalOctaves = m_octaves;
		nls.fractalLacunarity = SIMDf_SET(m_lacunarity);
		nls.fractalGain = SIMDf_SET(m_gain);
		nls.fractalBounding = SIMDf_SET(m_fractalBounding);

		switch (m_cellularDistanceFunction)
		{
		case Euclidean:
			SET_BUILDER(result = FUNC(CellularLookupEuclideanSingle)(seedV, xF, yF, zF, cellJitterV, nls))
				break; \
		case Manhattan:
			SET_BUILDER(result = FUNC(CellularLookupManhattanSingle)(seedV, xF, yF, zF, cellJitterV, nls))
				break; \
		case Natural:
			SET_BUILDER(result = FUNC(CellularLookupNaturalSingle)(seedV, xF, yF, zF, cellJitterV, nls))
				break;
		}
		break;
	}
	SIMD_ZERO_ALL();
}

#define CELLULAR_MULTI_VECTOR(returnFunc)\
switch(m_cellularDistanceFunction)\
{\
case Euclidean:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##EuclideanSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
case Manhattan:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##ManhattanSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
case Natural:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##NaturalSingle)(seedV, xF, yF, zF, cellJitterV))\
	break;\
}

#define CELLULAR_INDEX_MULTI_VECTOR(returnFunc)\
switch(m_cellularDistanceFunction)\
{\
case Euclidean:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##EuclideanSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
case Manhattan:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##ManhattanSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
case Natural:\
	VECTOR_SET_BUILDER(result = FUNC(Cellular##returnFunc##NaturalSingle)(seedV, xF, yF, zF, cellJitterV, m_cellularDistanceIndex0, m_cellularDistanceIndex1))\
	break;\
}

void SIMD_LEVEL_CLASS::FillCellularSet(float* noiseSet, FastNoiseVectorSet* vectorSet, float xOffset, float yOffset, float zOffset)
{
	assert(noiseSet);
	assert(vectorSet);
	assert(vectorSet->size >= 0);
	SIMD_ZERO_ALL();

	SIMDi seedV = SIMDi_SET(m_seed);
	SIMDf xFreqV = SIMDf_SET(m_frequency * m_xScale);
	SIMDf yFreqV = SIMDf_SET(m_frequency * m_yScale);
	SIMDf zFreqV = SIMDf_SET(m_frequency * m_zScale);
	SIMDf xOffsetV = SIMDf_MUL(SIMDf_SET(xOffset), xFreqV);
	SIMDf yOffsetV = SIMDf_MUL(SIMDf_SET(yOffset), yFreqV);
	SIMDf zOffsetV = SIMDf_MUL(SIMDf_SET(zOffset), zFreqV);
	SIMDf cellJitterV = SIMDf_SET(m_cellularJitter);
	INIT_PERTURB_VALUES();

	int index = 0;
	int loopMax = vectorSet->size SIZE_MASK;
	NoiseLookupSettings nls;

	switch (m_cellularReturnType)
	{
	case CellValue:
		CELLULAR_MULTI_VECTOR(Value);
		break;
	case Distance:
		CELLULAR_MULTI_VECTOR(Distance);
		break;
	case Distance2:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2);
		break;
	case Distance2Add:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2Add);
		break;
	case Distance2Sub:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2Sub);
		break;
	case Distance2Mul:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2Mul);
		break;
	case Distance2Div:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2Div);
		break;
	case Distance2Cave:
		CELLULAR_INDEX_MULTI_VECTOR(Distance2Cave);
		break;
	case NoiseLookup:
		nls.type = m_cellularNoiseLookupType;
		nls.frequency = SIMDf_SET(m_cellularNoiseLookupFrequency);
		nls.fractalType = m_fractalType;
		nls.fractalOctaves = m_octaves;
		nls.fractalLacunarity = SIMDf_SET(m_lacunarity);
		nls.fractalGain = SIMDf_SET(m_gain);
		nls.fractalBounding = SIMDf_SET(m_fractalBounding);

		switch (m_cellularDistanceFunction)
		{
		case Euclidean:
			VECTOR_SET_BUILDER(result = FUNC(CellularLookupEuclideanSingle)(seedV, xF, yF, zF, cellJitterV, nls));
			break;
		case Manhattan:
			VECTOR_SET_BUILDER(result = FUNC(CellularLookupManhattanSingle)(seedV, xF, yF, zF, cellJitterV, nls));
			break;
		case Natural:
			VECTOR_SET_BUILDER(result = FUNC(CellularLookupNaturalSingle)(seedV, xF, yF, zF, cellJitterV, nls));
			break;
		}
		break;
	}
	SIMD_ZERO_ALL();
}

#define SAMPLE_INDEX(_x,_y,_z) ((_x) * yzSizeSample + (_y) * zSizeSample + (_z))
#define SET_INDEX(_x,_y,_z) ((_x) * yzSize + (_y) * zSize + (_z))

void SIMD_LEVEL_CLASS::FillSampledNoiseSet(float* noiseSet, int xStart, int yStart, int zStart, int xSize, int ySize, int zSize, int sampleScale)
{
	assert(noiseSet);
	SIMD_ZERO_ALL();

	if (sampleScale <= 0)
	{
		FillNoiseSet(noiseSet, xStart, yStart, zStart, xSize, ySize, zSize);
		return;
	}

	int sampleSize = 1 << sampleScale;
	int sampleMask = sampleSize - 1;
	float scaleModifier = float(sampleSize);

	int xOffset = (sampleSize - (xStart & sampleMask)) & sampleMask;
	int yOffset = (sampleSize - (yStart & sampleMask)) & sampleMask;
	int zOffset = (sampleSize - (zStart & sampleMask)) & sampleMask;

	int xSizeSample = xSize + xOffset;
	int ySizeSample = ySize + yOffset;
	int zSizeSample = zSize + zOffset;

	if (xSizeSample & sampleMask)
		xSizeSample = (xSizeSample & ~sampleMask) + sampleSize;

	if (ySizeSample & sampleMask)
		ySizeSample = (ySizeSample & ~sampleMask) + sampleSize;

	if (zSizeSample & sampleMask)
		zSizeSample = (zSizeSample & ~sampleMask) + sampleSize;

	xSizeSample = (xSizeSample >> sampleScale) + 1;
	ySizeSample = (ySizeSample >> sampleScale) + 1;
	zSizeSample = (zSizeSample >> sampleScale) + 1;

	float* noiseSetSample = GetEmptySet(xSizeSample * ySizeSample * zSizeSample);
	FillNoiseSet(noiseSetSample, xStart >> sampleScale, yStart >> sampleScale, zStart >> sampleScale, xSizeSample, ySizeSample, zSizeSample, scaleModifier);

	int yzSizeSample = ySizeSample * zSizeSample;
	int yzSize = ySize * zSize;

	SIMDi axisMask = SIMDi_SET(sampleMask);
	SIMDf axisScale = SIMDf_SET(1.f / scaleModifier);
	SIMDf axisOffset = SIMDf_MUL(axisScale, SIMDf_NUM(0_5));

	SIMDi sampleSizeSIMD = SIMDi_SET(sampleSize);
	SIMDi xSIMD = SIMDi_SET(-xOffset);
	SIMDi yBase = SIMDi_SET(-yOffset);
	SIMDi zBase = SIMDi_SET(-zOffset);

	int localCountMax = (1 << (sampleScale * 3));
	int vMax = VECTOR_SIZE;

#if SIMD_LEVEL == FN_NEON
	SIMDi sampleScaleV = SIMDi_SET(-sampleScale);
	SIMDi sampleScale2V = SIMDi_MUL(sampleScaleV, SIMDi_NUM(2));
#endif

	for (int x = 0; x < xSizeSample - 1; x++)
	{
		SIMDi ySIMD = yBase;
		for (int y = 0; y < ySizeSample - 1; y++)
		{
			SIMDi zSIMD = zBase;

			SIMDf c001 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y, 0)]);
			SIMDf c101 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y, 0)]);
			SIMDf c011 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y + 1, 0)]);
			SIMDf c111 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y + 1, 0)]);
			for (int z = 0; z < zSizeSample - 1; z++)
			{
				SIMDf c000 = c001;
				SIMDf c100 = c101;
				SIMDf c010 = c011;
				SIMDf c110 = c111;
				c001 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y, z + 1)]);
				c101 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y, z + 1)]);
				c011 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y + 1, z + 1)]);
				c111 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y + 1, z + 1)]);

				SIMDi localCountSIMD = SIMDi_NUM(incremental);

				int localCount = 0;
				while (localCount < localCountMax)
				{
					uSIMDi xi, yi, zi;

#if SIMD_LEVEL == FN_NEON
					xi.m = SIMDi_AND(SIMDi_VSHIFT_L(localCountSIMD, sampleScale2V), axisMask);
					yi.m = SIMDi_AND(SIMDi_VSHIFT_L(localCountSIMD, sampleScaleV), axisMask);
#else
					xi.m = SIMDi_AND(SIMDi_SHIFT_R(localCountSIMD, sampleScale * 2), axisMask);
					yi.m = SIMDi_AND(SIMDi_SHIFT_R(localCountSIMD, sampleScale), axisMask);
#endif

					zi.m = SIMDi_AND(localCountSIMD, axisMask);

					SIMDf xf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(xi.m), axisScale, axisOffset);
					SIMDf yf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(yi.m), axisScale, axisOffset);
					SIMDf zf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(zi.m), axisScale, axisOffset);

					xi.m = SIMDi_ADD(xi.m, xSIMD);
					yi.m = SIMDi_ADD(yi.m, ySIMD);
					zi.m = SIMDi_ADD(zi.m, zSIMD);

					uSIMDf sampledResults;
					sampledResults.m = FUNC(Lerp)(
						FUNC(Lerp)(
							FUNC(Lerp)(c000, c100, xf),
							FUNC(Lerp)(c010, c110, xf), yf),
						FUNC(Lerp)(
							FUNC(Lerp)(c001, c101, xf),
							FUNC(Lerp)(c011, c111, xf), yf), zf);

					for (int i = 0; i < vMax; i++)
					{
						if (xi.a[i] >= 0 && xi.a[i] < xSize &&
							yi.a[i] >= 0 && yi.a[i] < ySize &&
							zi.a[i] >= 0 && zi.a[i] < zSize)
						{
							int index = SET_INDEX(xi.a[i], yi.a[i], zi.a[i]);
							noiseSet[index] = sampledResults.a[i];
						}
					}

					localCount += VECTOR_SIZE;
					localCountSIMD = SIMDi_ADD(localCountSIMD, SIMDi_NUM(vectorSize));
				}
				zSIMD = SIMDi_ADD(zSIMD, sampleSizeSIMD);
			}
			ySIMD = SIMDi_ADD(ySIMD, sampleSizeSIMD);
		}
		xSIMD = SIMDi_ADD(xSIMD, sampleSizeSIMD);
	}

	FreeNoiseSet(noiseSetSample);
	SIMD_ZERO_ALL();
}

void SIMD_LEVEL_CLASS::FillSampledNoiseSet(float* noiseSet, FastNoiseVectorSet* vectorSet, float xOffset, float yOffset, float zOffset)
{
	assert(noiseSet);
	assert(vectorSet);
	assert(vectorSet->size >= 0);
	SIMD_ZERO_ALL();

	int sampleScale = vectorSet->sampleScale;

	if (sampleScale <= 0)
	{
		FillNoiseSet(noiseSet, vectorSet, xOffset, yOffset, zOffset);
		return;
	}

	int sampleSize = 1 << sampleScale;
	int sampleMask = sampleSize - 1;
	float scaleModifier = float(sampleSize);

	int xSize = vectorSet->sampleSizeX;
	int ySize = vectorSet->sampleSizeY;
	int zSize = vectorSet->sampleSizeZ;

	int xSizeSample = xSize;
	int ySizeSample = ySize;
	int zSizeSample = zSize;

	if (xSizeSample & sampleMask)
		xSizeSample = (xSizeSample & ~sampleMask) + sampleSize;

	if (ySizeSample & sampleMask)
		ySizeSample = (ySizeSample & ~sampleMask) + sampleSize;

	if (zSizeSample & sampleMask)
		zSizeSample = (zSizeSample & ~sampleMask) + sampleSize;

	xSizeSample = (xSizeSample >> sampleScale) + 1;
	ySizeSample = (ySizeSample >> sampleScale) + 1;
	zSizeSample = (zSizeSample >> sampleScale) + 1;

	float* noiseSetSample = GetEmptySet(vectorSet->size);
	FillNoiseSet(noiseSetSample, vectorSet, xOffset - 0.5f, yOffset - 0.5f, zOffset - 0.5f);

	int yzSizeSample = ySizeSample * zSizeSample;
	int yzSize = ySize * zSize;

	SIMDi axisMask = SIMDi_SET(sampleMask);
	SIMDf axisScale = SIMDf_SET(1.f / scaleModifier);
	SIMDf axisOffset = SIMDf_MUL(axisScale, SIMDf_NUM(0_5));

	SIMDi sampleSizeSIMD = SIMDi_SET(sampleSize);
	SIMDi xSIMD = SIMDi_SET_ZERO();

	int localCountMax = (1 << (sampleScale * 3));
	int vMax = VECTOR_SIZE;

#if SIMD_LEVEL == FN_NEON
	SIMDi sampleScaleV = SIMDi_SET(-sampleScale);
	SIMDi sampleScale2V = SIMDi_MUL(sampleScaleV, SIMDi_NUM(2));
#endif

	for (int x = 0; x < xSizeSample - 1; x++)
	{
		SIMDi ySIMD = SIMDi_SET_ZERO();
		for (int y = 0; y < ySizeSample - 1; y++)
		{
			SIMDi zSIMD = SIMDi_SET_ZERO();

			SIMDf c001 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y, 0)]);
			SIMDf c101 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y, 0)]);
			SIMDf c011 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y + 1, 0)]);
			SIMDf c111 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y + 1, 0)]);
			for (int z = 0; z < zSizeSample - 1; z++)
			{
				SIMDf c000 = c001;
				SIMDf c100 = c101;
				SIMDf c010 = c011;
				SIMDf c110 = c111;
				c001 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y, z + 1)]);
				c101 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y, z + 1)]);
				c011 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x, y + 1, z + 1)]);
				c111 = SIMDf_SET(noiseSetSample[SAMPLE_INDEX(x + 1, y + 1, z + 1)]);

				SIMDi localCountSIMD = SIMDi_NUM(incremental);

				int localCount = 0;
				while (localCount < localCountMax)
				{
					uSIMDi xi, yi, zi;

#if SIMD_LEVEL == FN_NEON
					xi.m = SIMDi_AND(SIMDi_VSHIFT_L(localCountSIMD, sampleScale2V), axisMask);
					yi.m = SIMDi_AND(SIMDi_VSHIFT_L(localCountSIMD, sampleScaleV), axisMask);
#else
					xi.m = SIMDi_AND(SIMDi_SHIFT_R(localCountSIMD, sampleScale * 2), axisMask);
					yi.m = SIMDi_AND(SIMDi_SHIFT_R(localCountSIMD, sampleScale), axisMask);
#endif

					zi.m = SIMDi_AND(localCountSIMD, axisMask);

					SIMDf xf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(xi.m), axisScale, axisOffset);
					SIMDf yf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(yi.m), axisScale, axisOffset);
					SIMDf zf = SIMDf_MUL_ADD(SIMDf_CONVERT_TO_FLOAT(zi.m), axisScale, axisOffset);

					xi.m = SIMDi_ADD(xi.m, xSIMD);
					yi.m = SIMDi_ADD(yi.m, ySIMD);
					zi.m = SIMDi_ADD(zi.m, zSIMD);

					uSIMDf sampledResults;
					sampledResults.m = FUNC(Lerp)(
						FUNC(Lerp)(
							FUNC(Lerp)(c000, c100, xf),
							FUNC(Lerp)(c010, c110, xf), yf),
						FUNC(Lerp)(
							FUNC(Lerp)(c001, c101, xf),
							FUNC(Lerp)(c011, c111, xf), yf), zf);

					for (int i = 0; i < vMax; i++)
					{
						if (xi.a[i] < xSize &&
							yi.a[i] < ySize &&
							zi.a[i] < zSize)
						{
							int index = SET_INDEX(xi.a[i], yi.a[i], zi.a[i]);
							noiseSet[index] = sampledResults.a[i];
						}
					}

					localCount += VECTOR_SIZE;
					localCountSIMD = SIMDi_ADD(localCountSIMD, SIMDi_NUM(vectorSize));
				}
				zSIMD = SIMDi_ADD(zSIMD, sampleSizeSIMD);
			}
			ySIMD = SIMDi_ADD(ySIMD, sampleSizeSIMD);
		}
		xSIMD = SIMDi_ADD(xSIMD, sampleSizeSIMD);
	}

	FreeNoiseSet(noiseSetSample);
	SIMD_ZERO_ALL();
}

#undef SIMD_LEVEL
#endif
