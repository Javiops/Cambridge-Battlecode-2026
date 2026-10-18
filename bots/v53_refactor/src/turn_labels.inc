const char* slot_name(Slot k) {
    switch (k) {
        case Slot::Reset: return "reset";
        case Slot::Dash: return "dash";
        case Slot::Targeted: return "target";
        case Slot::Ground: return "ground";
        case Slot::Heal: return "heal";
        case Slot::Shield: return "shield";
        default: return "none";
    }
}

