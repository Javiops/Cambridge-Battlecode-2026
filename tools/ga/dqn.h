// Deep Q-network for the fight micro (tools/ga/dqn.py). Copied into the bot's src/ by the tool, next to ga_struct.h.
//
// While enemies are in sight (the same place where the level-3 NEAT net of ga_struct.h acts), a small dense net
// reads the 25 fight features (GaFeat) and scores the 7 actions of ga_struct.h:
//   0 default (let the rules decide), 1 engage, 2 kite, 3 back off, 4 flee, 5 recall, 6 farm.
// The bot plays the argmax, or a random valid action with probability epsilon (data collection only).
// With logging on it prints one line per decision ([dq]) and one per turn while a contact lasts ([dt]); dqn.py turns
// those lines into transitions (state, action, reward, next state) and trains the net offline in Python.
//
// The genome is the patchable volatile array dq_g (magic 'DQN1'): flags, then the weights x DQ_SCALE. All zero = Q
// is 0 for every action = argmax picks 0 = the rules decide = the control bot.
#pragma once
#include <cstdint>
#include <cstdio>
#include <cmath>
#include <optional>

#define DQ_IN GF_N
#define DQ_H 32
#define DQ_OUT GA_NN_OUT
#define DQ_SCALE 4096.0f
// header: on (mode), epsilon (per mille), log, seed, hidden units used (<= DQ_H), margin (Q of an action must beat
// Q(default) by this x 1/1000 to replace the rules)
#define DQ_HDR 6
#define DQ_LEN (DQ_HDR + DQ_H * DQ_IN + DQ_H + DQ_OUT * DQ_H + DQ_OUT)

#ifndef DQ_HAVE_GENOME
static const int dq_zero[DQ_LEN] = {0};
#define DQ_G (dq_zero)
#endif

struct DqState {
    bool init = false;
    bool on = false, log = false;
    int mode = 0;  // 1 Q-network argmax; 4 PPO policy (softmax sample over the outputs as logits); 2 / 3 death-risk value: back off / flee when p(die) > margin per mille
    int eps = 0, hid = 0, margin = 0;
    uint32_t rng = 1;
    float w1[DQ_H][DQ_IN], b1[DQ_H], w2[DQ_OUT][DQ_H], b2[DQ_OUT];
    int last_dec = -1000;  // round of the last decision (contact window for the [dt] trace)
    char name[16] = {0};   // champion name: every champion of the team prints into the same stdout
};
static DqState g_dq;

inline void dq_load(const char* name) {
    DqState& d = g_dq;
    if (d.init) return;
    d.init = true;
    const volatile int* g = DQ_G;
    d.on = g[0] != 0;
    d.mode = g[0];
    d.eps = g[1];
    d.log = g[2] != 0;
    d.rng = static_cast<uint32_t>(g[3]) * 2654435761u + 12345u;
    for (const char* c = name; *c; ++c) d.rng = d.rng * 31u + static_cast<uint8_t>(*c);
    std::snprintf(d.name, sizeof d.name, "%s", name);
    if (!d.rng) d.rng = 1;
    d.hid = g[4] < 0 ? 0 : (g[4] > DQ_H ? DQ_H : g[4]);
    d.margin = g[5];
    int k = DQ_HDR;
    for (int h = 0; h < DQ_H; ++h)
        for (int i = 0; i < DQ_IN; ++i) d.w1[h][i] = g[k++] / DQ_SCALE;
    for (int h = 0; h < DQ_H; ++h) d.b1[h] = g[k++] / DQ_SCALE;
    for (int o = 0; o < DQ_OUT; ++o)
        for (int h = 0; h < DQ_H; ++h) d.w2[o][h] = g[k++] / DQ_SCALE;
    for (int o = 0; o < DQ_OUT; ++o) d.b2[o] = g[k++] / DQ_SCALE;
}

inline uint32_t dq_rand() {
    uint32_t x = g_dq.rng;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return g_dq.rng = x;
}

// Q values of the 7 actions (inputs scaled like the NEAT net: feature / ga_feat_scale).
inline void dq_q(const int* feat, float* q) {
    const DqState& d = g_dq;
    float x[DQ_IN], h[DQ_H];
    for (int i = 0; i < DQ_IN; ++i) x[i] = feat[i] / ga_feat_scale[i];
    for (int j = 0; j < d.hid; ++j) {
        float s = d.b1[j];
        for (int i = 0; i < DQ_IN; ++i) s += d.w1[j][i] * x[i];
        h[j] = s > 0 ? s : 0;
    }
    for (int o = 0; o < DQ_OUT; ++o) {
        float s = d.b2[o];
        for (int j = 0; j < d.hid; ++j) s += d.w2[o][j] * h[j];
        q[o] = s;
    }
}

// The action to play. valid = bit mask of the actions that can act now (bit 0 always set).
// *greedy = 0 when epsilon picked it.
inline int dq_act(const int* feat, int valid, int* greedy) {
    const DqState& d = g_dq;
    *greedy = 1;
    if (d.eps > 0 && static_cast<int>(dq_rand() % 1000) < d.eps) {
        int n = 0, opts[DQ_OUT];
        for (int a = 0; a < DQ_OUT; ++a)
            if (valid >> a & 1) opts[n++] = a;
        *greedy = 0;
        return opts[dq_rand() % n];
    }
    if (d.hid <= 0) return 0;
    float q[DQ_OUT];
    dq_q(feat, q);
    if (d.mode == 4) {  // PPO: sample from softmax(Q as logits) over the valid actions; greedy = 10 + the sampled action
        float mx = -1e30f, p[DQ_OUT], sum = 0;
        for (int a = 0; a < DQ_OUT; ++a)
            if ((valid >> a & 1) && q[a] > mx) mx = q[a];
        for (int a = 0; a < DQ_OUT; ++a) {
            p[a] = (valid >> a & 1) ? std::exp(q[a] - mx) : 0.0f;
            sum += p[a];
        }
        float u = (dq_rand() % 1000000) / 1000000.0f * sum;
        int a = 0;
        for (; a < DQ_OUT - 1; ++a) {
            if (u < p[a]) break;
            u -= p[a];
        }
        while (a > 0 && !(valid >> a & 1)) --a;
        *greedy = 10 + a;
        return a;
    }
    if (d.mode >= 2) {  // q[0] = logit of dying within 10 rounds (tools/ga/fightval.py)
        float p = 1.0f / (1.0f + std::exp(-q[0]));
        return p * 1000.0f > d.margin ? (d.mode == 2 ? 3 : 4) : 0;
    }
    int best = 0;
    float bv = q[0] + d.margin / 1000.0f;
    for (int a = 1; a < DQ_OUT; ++a)
        if ((valid >> a & 1) && q[a] > bv) {
            bv = q[a];
            best = a;
        }
    return best;
}

// Per-turn trace while a contact lasts (from the first decision until 15 rounds after the last one), dead turns
// included, so dqn.py sees hp, gems and gold move and sees the death.
inline void dq_trace(int round, bool alive, float hp, float mhp, int gems, int gold,
                     const std::optional<cambc::team>& my, const std::optional<cambc::team>& en) {
    DqState& d = g_dq;
    if (!d.log || round - d.last_dec > 15) return;
    int ours = -1, theirs = -1;  // team scores (gems submitted): the reward can follow the real objective
    try {
        if (my && en) {
            ours = static_cast<int>(cambc::global_submitted_gems(*my));
            theirs = static_cast<int>(cambc::global_submitted_gems(*en));
        }
    } catch (...) {
    }
    // flushed at once: output still buffered when the turn ends is lost
    std::printf("[dt] %s %d %d %d %d %d %d %d %d\n", d.name, round, alive ? 1 : 0, static_cast<int>(hp),
                static_cast<int>(mhp), gems, gold, ours, theirs);
    std::fflush(stdout);
}

inline void dq_log_decision(int round, int act, int greedy, int valid, const int* feat) {
    DqState& d = g_dq;
    d.last_dec = round;
    if (!d.log) return;
    char buf[256];
    int n = std::snprintf(buf, sizeof buf, "[dq] %s %d %d %d %d", d.name, round, act, greedy, valid);
    for (int i = 0; i < DQ_IN && n < 240; ++i) n += std::snprintf(buf + n, sizeof buf - n, " %d", feat[i]);
    std::puts(buf);
    std::fflush(stdout);
}
