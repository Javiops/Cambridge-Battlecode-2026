#pragma once
#include <algorithm>
#include <array>
#include <charconv>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string_view>

namespace tactics {
// Locale-based iostream formatting for every field can spend an owner turn.
// These bounded records use one stdout write and no dynamic allocation.
class LogLine {
    std::array<char, 512> bytes_{};
    std::size_t size_ = 0;
    void append(std::string_view value) {
        const auto count = std::min(value.size(), bytes_.size() - size_ - 1);
        std::memcpy(bytes_.data() + size_, value.data(), count);
        size_ += count;
    }

  public:
    explicit LogLine(std::string_view prefix) {
        append(prefix);
    }
    LogLine &field(std::string_view value) {
        append(" ");
        append(value);
        return *this;
    }
    LogLine &field(std::int64_t value) {
        append(" ");
        const auto result =
            std::to_chars(bytes_.data() + size_, bytes_.data() + bytes_.size() - 1, value);
        if (result.ec == std::errc{})
            size_ = result.ptr - bytes_.data();
        return *this;
    }
    void emit() {
        bytes_[size_++] = '\n';
        std::fwrite(bytes_.data(), 1, size_, stdout);
    }
};
} // namespace tactics
