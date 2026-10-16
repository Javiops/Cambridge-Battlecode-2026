// Structure genes of the genetic algorithm (tools/ga/structure.py). Copied into the bot's src/ by the tool, never
// part of the uploaded bot unless a genome is exported.
//
// Level 1: every micro rule of play_turn has an on/off gene (P_R_*) and an order gene (P_O_*): the rules run
//          sorted by their order gene (ties keep the base order), the first one that acts ends the turn.
// Level 2: two evolved conditions (genetic programming), each a postfix program over the fight features:
//          GP0 replaces "back off from an unfavourable group" (rule AVOID), GP1 replaces "engage the target"
//          (rule ENGAGE). The program's result > 0 means yes.
// Level 3: a NEAT network over the same features picks one action per turn while enemies are in sight:
//          0 default (let the rules decide), 1 engage, 2 kite, 3 back off, 4 flee, 5 recall, 6 farm.
//
// The genome arrays live in params.h (`ga_s`, volatile, patched in the wasm); with no params.h every gene keeps
// the base behaviour.
#pragma once
#include <cmath>

// ---- level 1 defaults (the base bot) ----
#ifndef P_R_FLEE
#define P_R_FLEE 1
#endif
#ifndef P_R_NEARRECALL
#define P_R_NEARRECALL 1
#endif
#ifndef P_R_AVOIDLOW
#define P_R_AVOIDLOW 1
#endif
#ifndef P_R_AVOID
#define P_R_AVOID 1
#endif
#ifndef P_R_ENGAGE
#define P_R_ENGAGE 1
#endif
#ifndef P_R_RECALLSHOP
#define P_R_RECALLSHOP 1
#endif
// order genes: the base order is FLEE, NEARRECALL, FM, KITE, FRONT, AVOIDLOW, AVOID, ENGAGE, RECALLSHOP, WALKHOME
#ifndef P_O_FLEE
#define P_O_FLEE 10
#endif
#ifndef P_O_NEARRECALL
#define P_O_NEARRECALL 20
#endif
#ifndef P_O_FM
#define P_O_FM 30
#endif
#ifndef P_O_KITE
#define P_O_KITE 40
#endif
#ifndef P_O_FRONT
#define P_O_FRONT 50
#endif
#ifndef P_O_AVOIDLOW
#define P_O_AVOIDLOW 60
#endif
#ifndef P_O_AVOID
#define P_O_AVOID 70
#endif
#ifndef P_O_ENGAGE
#define P_O_ENGAGE 80
#endif
#ifndef P_O_RECALLSHOP
#define P_O_RECALLSHOP 90
#endif
#ifndef P_O_WALKHOME
#define P_O_WALKHOME 100
#endif
// ---- level 2 / 3 switches ----
#ifndef P_GP0_ON
#define P_GP0_ON 0
#endif
#ifndef P_GP1_ON
#define P_GP1_ON 0
#endif
#ifndef P_NN_ON
#define P_NN_ON 0
#endif

enum GaRule { GR_FLEE, GR_NEARRECALL, GR_FM, GR_KITE, GR_FRONT, GR_AVOIDLOW, GR_AVOID, GR_ENGAGE, GR_RECALLSHOP,
              GR_WALKHOME, GR_N };

// The rule order of this genome: stable sort by order gene.
inline void ga_rule_order(int* out) {
    const int pr[GR_N] = {P_O_FLEE, P_O_NEARRECALL, P_O_FM, P_O_KITE, P_O_FRONT, P_O_AVOIDLOW, P_O_AVOID,
                          P_O_ENGAGE, P_O_RECALLSHOP, P_O_WALKHOME};
    for (int i = 0; i < GR_N; ++i) out[i] = i;
    for (int i = 1; i < GR_N; ++i)
        for (int j = i; j > 0 && pr[out[j - 1]] > pr[out[j]]; --j) {
            int t = out[j];
            out[j] = out[j - 1];
            out[j - 1] = t;
        }
}

// ---- fight features (level 2 terminals and level 3 inputs); keep in sync with structure.py FEATURES ----
enum GaFeat {
    GF_HP,         // our hp %
    GF_NEAR,       // nearest enemy champion, tiles (capped 20)
    GF_F4, GF_F8,  // enemy champions within 4 / 8
    GF_A4, GF_A8,  // allies within 4 / 8 (me not counted)
    GF_RATIO,      // our hp within 6 (me included) / their hp within 8, %  (capped 999)
    GF_ERATIO,     // around the target: our hp within 8 of it / theirs, % (GF_RATIO when no target)
    GF_FAV,        // the base rule's "favourable" (0/1)
    GF_KILL,       // target killable (0/1)
    GF_REACH,      // target within attack range + 1 (0/1)
    GF_THP,        // target hp % of its max (100 with no target)
    GF_TDIST,      // target distance (20 with no target)
    GF_GEMS,       // gems carried
    GF_HOME,       // distance to our spawn centre
    GF_DANGER,     // ready enemy damage on our tile, % of our hp (capped 999)
    GF_SPAWN,      // standing on our spawn (0/1)
    GF_TCHAN,      // target channelling (0/1)
    GF_HELP,       // an ally asked for help / gang target (0/1)
    GF_CASTERS,    // caster draft (0/1)
    GF_ROUND,      // round / 10
    GF_HIT,        // we were hit this round or the last (0/1)
    GF_NB, GF_EB,  // champions of ours / theirs within 8 of the target (me included; 1 / 0 with no target)
    GF_RANGED,     // our attack range > 1 (0/1)
    GF_N
};
// level 3 input scale: input = feature / scale
static const float ga_feat_scale[GF_N] = {100, 10, 3, 3, 3, 3, 200, 200, 1, 1, 1, 100, 10, 50, 20, 100, 1, 1, 1,
                                          1, 200, 1, 3, 3, 1};

// ---- level 2: postfix program. prog[0] = length, then tokens: op = t & 31, arg = t >> 5 ----
enum GaOp { GO_VAR = 1, GO_CONST, GO_ADD, GO_SUB, GO_MUL, GO_MIN, GO_MAX, GO_LT, GO_AND, GO_OR, GO_NOT, GO_IF, GO_GT };
#define GA_PROG_LEN 48

inline long ga_run(const volatile int* prog, const int* feat) {
    int n = prog[0];
    if (n <= 0 || n >= GA_PROG_LEN) return 0;
    long st[24];
    int sp = 0;
    for (int i = 1; i <= n; ++i) {
        int t = prog[i];
        int op = t & 31, a = t >> 5;
        if (op == GO_VAR || op == GO_CONST) {
            if (sp >= 24) return 0;
            st[sp++] = op == GO_CONST ? a : (a >= 0 && a < GF_N ? feat[a] : 0);
            continue;
        }
        if (op == GO_NOT) {
            if (sp < 1) return 0;
            st[sp - 1] = st[sp - 1] > 0 ? 0 : 1;
            continue;
        }
        if (op == GO_IF) {
            if (sp < 3) return 0;
            long c = st[sp - 3], x = st[sp - 2], y = st[sp - 1];
            sp -= 2;
            st[sp - 1] = c > 0 ? x : y;
            continue;
        }
        if (sp < 2) return 0;
        long x = st[sp - 2], y = st[sp - 1], r = 0;
        switch (op) {
            case GO_ADD: r = x + y; break;
            case GO_SUB: r = x - y; break;
            case GO_MUL: r = x * y / 100; break;
            case GO_MIN: r = x < y ? x : y; break;
            case GO_MAX: r = x > y ? x : y; break;
            case GO_LT: r = x < y; break;
            case GO_GT: r = x > y; break;
            case GO_AND: r = x > 0 && y > 0; break;
            case GO_OR: r = x > 0 || y > 0; break;
            default: return 0;
        }
        if (r > 1000000) r = 1000000;
        if (r < -1000000) r = -1000000;
        --sp;
        st[sp - 1] = r;
    }
    return sp ? st[sp - 1] : 0;
}

// ---- level 3: feed-forward net in topological order ----
// nn[0] = computed nodes (hidden + outputs, outputs last), nn[1] = connections, nn[2 .. 2+GA_NN_NODES) = bias x1000,
// then GA_NN_CONN triples (src node, dst node, weight x1000) sorted by dst. Node ids: 0..GF_N-1 inputs, then the
// computed nodes in order; src < dst always. Hidden nodes use tanh, outputs are linear; the action is the argmax.
#define GA_NN_NODES 32
#define GA_NN_CONN 128
#define GA_NN_OUT 7
#define GA_NN_LEN (2 + GA_NN_NODES + 3 * GA_NN_CONN)

inline int ga_nn_act(const volatile int* nn, const int* feat) {
    int nodes = nn[0], conns = nn[1];
    if (nodes < GA_NN_OUT || nodes > GA_NN_NODES || conns < 0 || conns > GA_NN_CONN) return 0;
    float act[GF_N + GA_NN_NODES];
    for (int i = 0; i < GF_N; ++i) act[i] = feat[i] / ga_feat_scale[i];
    const volatile int* cn = nn + 2 + GA_NN_NODES;
    int c = 0;
    for (int j = 0; j < nodes; ++j) {
        int id = GF_N + j;
        float s = nn[2 + j] / 1000.0f;
        while (c < conns && cn[3 * c + 1] == id) {
            int src = cn[3 * c];
            if (src >= 0 && src < id) s += act[src] * (cn[3 * c + 2] / 1000.0f);
            ++c;
        }
        act[id] = j < nodes - GA_NN_OUT ? std::tanh(s) : s;
    }
    int best = 0;
    float bv = act[GF_N + nodes - GA_NN_OUT];
    for (int k = 1; k < GA_NN_OUT; ++k)
        if (act[GF_N + nodes - GA_NN_OUT + k] > bv) {
            bv = act[GF_N + nodes - GA_NN_OUT + k];
            best = k;
        }
    return best;
}

#ifndef GA_HAVE_GENOME
static const int ga_s_zero[GA_PROG_LEN * 2 + GA_NN_LEN] = {0};
#define GA_GP0 (ga_s_zero)
#define GA_GP1 (ga_s_zero + GA_PROG_LEN)
#define GA_NN (ga_s_zero + 2 * GA_PROG_LEN)
#endif
