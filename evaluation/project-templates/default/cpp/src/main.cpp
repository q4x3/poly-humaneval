#include <fstream>
#include <cmath>
#include <climits>
#include <cctype>
#include <ctime>
#include <algorithm>
#include <bitset>
#include <deque>
#include <functional>
#include <iomanip>
#include <iterator>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <utility>
#include <vector>
#include <chrono>
#include <regex>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <optional>
#include <variant>
#include <any>
#include <format>
#include <cassert>

using namespace std;

namespace utils {
    string escapeString(string str);
    class PolyEvalType;
    string genVoid(nullptr_t value);
    string genInt(int value);
    string genLong(long long value);
    string genDouble(double value);
    string genBool(bool value);
    string genChar(char value);
    string genString(string value);
    string genAny(any value);
    template<typename T> string genList(const vector<T> &value, unique_ptr<PolyEvalType>& t);
    template<typename T> string genMlist(const vector<T> &value, unique_ptr<PolyEvalType>& t);
    template<typename T> string genUnorderedlist(const vector<T> &value, unique_ptr<PolyEvalType>& t);
    template<typename K, typename V> string genDict(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t);
    template<typename K, typename V> string genMdict(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t);
    template<typename T> string genOptional(const optional<T> &value, unique_ptr<PolyEvalType>& t);

    template<typename T> string toPolyEvalStr(T value, unique_ptr<PolyEvalType>& t);
    template<typename T> string toPolyEvalStr(const vector<T> &value, unique_ptr<PolyEvalType>& t);
    template<typename K, typename V> string toPolyEvalStr(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t);
    template<typename T> string toPolyEvalStr(const optional<T> &value, unique_ptr<PolyEvalType>& t);

    template<typename T> string toPolyEvalStrWithType(T value, unique_ptr<PolyEvalType>& t);
    template<typename T> string toPolyEvalStrWithType(const vector<T> &value, unique_ptr<PolyEvalType>& t);
    template<typename K, typename V> string toPolyEvalStrWithType(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t);
    template<typename T> string toPolyEvalStrWithType(const optional<T> &value, unique_ptr<PolyEvalType>& t);

    template<typename T> string myStringify(T value, string type_str);
    template<typename T> string myStringify(const vector<T> &value, string type_str);
    template<typename K, typename V> string myStringify(const unordered_map<K, V> &value, string type_str);
    template<typename T> string myStringify(const optional<T> &value, string type_str);

    class PolyEvalType {
    public:
        string typeStr;
        string typeName;
        unique_ptr<PolyEvalType> valueType;
        unique_ptr<PolyEvalType> keyType;
        PolyEvalType(string type_str){
            typeStr = type_str;
            if (type_str.find("<") == string::npos) {
                typeName = type_str;
                return;
            } else {
                int idx = type_str.find("<");
                typeName = type_str.substr(0, idx);
                string other_str = type_str.substr(idx + 1, type_str.length() - idx - 2);
                if (other_str.find(",") == string::npos) {
                    valueType = std::make_unique<PolyEvalType>(other_str);
                } else {
                    idx = other_str.find(",");
                    keyType = std::make_unique<PolyEvalType>(other_str.substr(0, idx));
                    valueType = std::make_unique<PolyEvalType>(other_str.substr(idx + 1));
                }
            }

        }
    };

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

    template<typename T> string genList(const vector<T> &value, unique_ptr<PolyEvalType>& t){
        vector<string> v_strs;
        if constexpr (is_same_v<T, bool>) {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType((bool)v, (*t).valueType));
            }
        } else {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType(v, (*t).valueType));
            }
        }
        string v_str = "";
        for (int i = 0; i < v_strs.size(); i++) {
            v_str += v_strs[i];
            if (i != v_strs.size() - 1) {
                v_str += ", ";
            }
        }
        return "[" + v_str + "]";
    }

    template<typename T> string genMlist(const vector<T> &value, unique_ptr<PolyEvalType>& t){
        vector<string> v_strs;
        if constexpr (is_same_v<T, bool>) {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType((bool)v, (*t).valueType));
            }
        } else {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType(v, (*t).valueType));
            }
        }
        string v_str = "";
        for (int i = 0; i < v_strs.size(); i++) {
            v_str += v_strs[i];
            if (i != v_strs.size() - 1) {
                v_str += ", ";
            }
        }
        return "[" + v_str + "]";
    }

    template<typename T> string genUnorderedlist(const vector<T> &value, unique_ptr<PolyEvalType>& t){
        vector<string> v_strs;
        if constexpr (is_same_v<T, bool>) {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType((bool)v, (*t).valueType));
            }
        } else {
            for (auto v : value) {
                v_strs.push_back(toPolyEvalStrWithType(v, (*t).valueType));
            }
        }
        sort(v_strs.begin(), v_strs.end());
        string v_str = "";
        for (int i = 0; i < v_strs.size(); i++) {
            v_str += v_strs[i];
            if (i != v_strs.size() - 1) {
                v_str += ", ";
            }
        }
        return "[" + v_str + "]";
    }

    template<typename K, typename V> string genDict(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t){
        vector<string> v_strs;
        for (auto [key, val] : value) {
            string k_str = toPolyEvalStrWithType(key, (*t).keyType);
            string v_str = toPolyEvalStrWithType(val, (*t).valueType);
            v_strs.push_back(k_str + "=>" + v_str);
        }
        sort(v_strs.begin(), v_strs.end());
        string v_str = "";
        for (int i = 0; i < v_strs.size(); i++) {
            v_str += v_strs[i];
            if (i != v_strs.size() - 1) {
                v_str += ", ";
            }
        }
        return "{" + v_str + "}";
    }

    template<typename K, typename V> string genMdict(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t){
        vector<string> v_strs;
        for (auto [key, val] : value) {
            string k_str = toPolyEvalStrWithType(key, (*t).keyType);
            string v_str = toPolyEvalStrWithType(val, (*t).valueType);
            v_strs.push_back(k_str + "=>" + v_str);
        }
        sort(v_strs.begin(), v_strs.end());
        string v_str = "";
        for (int i = 0; i < v_strs.size(); i++) {
            v_str += v_strs[i];
            if (i != v_strs.size() - 1) {
                v_str += ", ";
            }
        }
        return "{" + v_str + "}";
    }

    template<typename T> string genOptional(const optional<T> &value, unique_ptr<PolyEvalType>& t){
        if (value.has_value()) {
            return toPolyEvalStr(value.value(), (*t).valueType);
        } else {
            return "null";
        }
    }

    template<typename T> string toPolyEvalStr(T value, unique_ptr<PolyEvalType>& t){
        string type_name = (*t).typeName;
        if (type_name == "void"){
            if constexpr (is_same_v<T, nullptr_t>) {
                return genVoid(value);
            }
        }
        else if (type_name == "int"){
            if constexpr (is_same_v<T, int>) {
                return genInt(value);
            }
        }
        else if (type_name == "long"){
            if constexpr (is_same_v<T, long long>) {
                return genLong(value);
            }
        }
        else if (type_name == "double"){
            if constexpr (is_same_v<T, double>) {
                return genDouble(value);
            }
        }
        else if (type_name == "bool"){
            if constexpr (is_same_v<T, bool>) {
                return genBool(value);
            }
        }
        else if (type_name == "char"){
            if constexpr (is_same_v<T, char>) {
                return genChar(value);
            }
        }
        else if (type_name == "string"){
            if constexpr (is_same_v<T, string>) {
                return genString(value);
            }
        }
        else if (type_name == "any"){
            if constexpr (is_same_v<T, any>) {
                return genAny(value);
            }
        }
        assert(false);
    }

    template<typename T> string toPolyEvalStr(const vector<T> &value, unique_ptr<PolyEvalType>& t){
        string type_name = (*t).typeName;
        if (type_name == "list"){
            return genList(value, t);
        }
        else if (type_name == "mlist"){
            return genMlist(value, t);
        }
        else if (type_name == "unorderedlist"){
            return genUnorderedlist(value, t);
        }
        assert(false);
    }

    template<typename K, typename V> string toPolyEvalStr(const unordered_map<K, V> &value, unique_ptr<PolyEvalType>& t){
        string type_name = (*t).typeName;
        if (type_name == "dict"){
            return genDict(value, t);
        }
        else if (type_name == "mdict"){
            return genMdict(value, t);
        }
        assert(false);
    }

    template<typename T> string toPolyEvalStr(const optional<T> &value, unique_ptr<PolyEvalType>& t){
        string type_name = (*t).typeName;
        if (type_name == "optional"){
            return genOptional(value, t);
        }
        assert(false);
    }

    template<typename T> string toPolyEvalStrWithType(T value, unique_ptr<PolyEvalType>& t){
        return toPolyEvalStr(value, t) + string(":") + (*t).typeStr;
    }

    template<typename T> string toPolyEvalStrWithType(const vector<T> &value, unique_ptr<PolyEvalType>& t){
        return toPolyEvalStr(value, t) + string(":") + (*t).typeStr;
    }

    template<typename K, typename V> string toPolyEvalStrWithType(const unordered_map<K,V> &value, unique_ptr<PolyEvalType>& t){
        return toPolyEvalStr(value, t) + string(":") + (*t).typeStr;
    }

    template<typename T> string toPolyEvalStrWithType(const optional<T> &value, unique_ptr<PolyEvalType>& t){
        return toPolyEvalStr(value, t) + string(":") + (*t).typeStr;
    }

    template<typename T> string myStringify(T value, string type_str){
        auto t = std::make_unique<PolyEvalType>(type_str);
        return toPolyEvalStrWithType(value, t);
    }

    template<typename T> string myStringify(const vector<T> &value, string type_str){
        auto t = std::make_unique<PolyEvalType>(type_str);
        return toPolyEvalStrWithType(value, t);
    }

    template<typename K, typename V> string myStringify(const unordered_map<K, V> &value, string type_str){
        auto t = std::make_unique<PolyEvalType>(type_str);
        return toPolyEvalStrWithType(value, t);
    }

    template<typename T> string myStringify(const optional<T> &value, string type_str){
        auto t = std::make_unique<PolyEvalType>(type_str);
        return toPolyEvalStrWithType(value, t);
    }
}

using utils::myStringify;

$$code$$