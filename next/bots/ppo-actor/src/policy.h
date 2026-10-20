#pragma once
#include <array>
#include <algorithm>
#include <cstdint>
#include <limits>
#include <wasm_simd128.h>

namespace actor {
constexpr int G=24,C=12,H=8,K=16,N=G*H+C*H+2*H+1;
using Features=std::array<float,G>;
using Candidate=std::array<float,C>;
struct Input { Features features{}; std::array<Candidate,K> candidates{}; std::array<bool,K> mask{}; int count=0; };
struct Result { std::array<float,K> scores{}; int chosen=0; };

struct Policy {
    alignas(16) std::array<float,N> weights{};
    // Feature-major four-lane SIMD; explicitly separate multiply/add for Python float32 parity.
    [[gnu::noinline]] Result evaluate(const Input& input) const {
        alignas(16) std::array<float,H> context{};
        const auto* wg=weights.data();const auto* wc=wg+G*H;
        const auto* bias=wc+C*H;const auto* out=bias+H;
        for(int h=0;h<H;h+=4) {
            auto a=wasm_v128_load(bias+h);
            for(int g=0;g<G;g++) a=wasm_f32x4_add(a,wasm_f32x4_mul(wasm_f32x4_splat(input.features[g]),wasm_v128_load(wg+g*H+h)));
            wasm_v128_store(context.data()+h,a);
        }
        Result result;float best=-std::numeric_limits<float>::infinity();
        // All padded rows are identical zeros. Evaluate one and copy its exact score.
        const int evaluated=std::min(K,input.count+1);
        for(int k=0;k<evaluated;k++) {
            auto sum=wasm_f32x4_splat(0);
            for(int h=0;h<H;h+=4) {
                auto a=wasm_v128_load(context.data()+h);
                for(int c=0;c<C;c++) a=wasm_f32x4_add(a,wasm_f32x4_mul(wasm_f32x4_splat(input.candidates[k][c]),wasm_v128_load(wc+c*H+h)));
                a=wasm_f32x4_max(a,wasm_f32x4_splat(0));
                sum=wasm_f32x4_add(sum,wasm_f32x4_mul(a,wasm_v128_load(out+h)));
            }
            result.scores[k]=((wasm_f32x4_extract_lane(sum,0)+wasm_f32x4_extract_lane(sum,1))+
                wasm_f32x4_extract_lane(sum,2))+wasm_f32x4_extract_lane(sum,3)+weights[N-1];
            if(input.mask[k] && result.scores[k]>best) {best=result.scores[k];result.chosen=k;}
        }
        for(int k=evaluated;k<K;k++)result.scores[k]=result.scores[evaluated-1];
        return result;
    }
};
}
