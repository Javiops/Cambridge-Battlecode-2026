// dummy-v1: the floor of the league. Drafts the first free champion, then never acts.
// Any real bot must beat it on every map; a bot that does not is broken, not unlucky.
#include <algorithm>
#include <cambc.h>

int main() {
    while (true) {
        if (cambc::is_draft()) {
            const auto chosen = cambc::draft::current_draft(cambc::team::ally);
            for (int i = 0; i < 11; ++i) {
                auto pick = static_cast<cambc::champion_draft>(i);
                if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
                    cambc::draft::pick(pick);
                    break;
                }
            }
        }
        cambc::end_turn();
    }
}
