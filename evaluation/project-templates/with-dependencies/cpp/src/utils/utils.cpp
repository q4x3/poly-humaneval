#include "utils.h"

namespace utils {
    string escapeString(string s) {
        string new_s;
        for (char c : s) {
            if (c == '\\') {
                new_s += "\\\\";
            } else if (c == '\"') {
                new_s += "\\\"";
            } else if (c == '\n') {
                new_s += "\\n";
            } else if (c == '\t') {
                new_s += "\\t";
            } else if (c == '\r') {
                new_s += "\\r";
            } else {
                new_s += c;
            }
        }
        return new_s;
    }

    string genVoid(nullptr_t value){
        return "null";
    }
    string genInt(int value) {
        return to_string(value);
    }
    string genLong(long long value){
        return to_string(value) + "L";
    }
    string genDouble(double value){
        if (isnan(value)) {
            return "nan";
        } else if (isinf(value)) {
            if (value > 0) {
                return "inf";
            } else {
                return "-inf";
            }
        }
        string value_str = to_string(value);
        if (value_str.find(".") != string::npos) {
            value_str = value_str.substr(0, value_str.find_last_not_of('0') + 1);
        }
        if (value_str[value_str.size() - 1] == '.') {
            value_str += "0";
        }
        if (value_str == "-0.0") {
            value_str = "0.0";
        }
        return value_str;
    }
    string genBool(bool value) {
        return value ? "true" : "false";
    }
    string genChar(char value){
        return "'" + escapeString(string(1, value)) + "'";
    }
    string genString(string value){
        return "\"" + escapeString(value) + "\"";
    }
    string genAny(any value) {
        if (value.type() == typeid(bool)) {
            return genBool(any_cast<bool>(value));
        } else if (value.type() == typeid(int)) {
            return genInt(any_cast<int>(value));
        } else if (value.type() == typeid(long long)) {
            return genLong(any_cast<long long>(value));
        } else if (value.type() == typeid(double)) {
            return genDouble(any_cast<double>(value));
        } else if (value.type() == typeid(char)) {
            return genChar(any_cast<char>(value));
        }else if (value.type() == typeid(string)) {
            return genString(any_cast<string>(value));
        }
        assert(false);
    }
}