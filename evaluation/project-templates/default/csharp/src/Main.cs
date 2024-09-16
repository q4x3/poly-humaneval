namespace Main;

using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Security.Cryptography;

using static Main.Utils;
using static Main.Global;

class Utils {
    private static string EscapeString(string s) {
        StringBuilder newS = new StringBuilder();
        for (int i = 0; i < s.Length; i++) {
            char c = s[i];
            switch(c) {
                case '\\':
                    newS.Append("\\\\");
                    break;
                case '\"':
                    newS.Append("\\\"");
                    break;
                case '\n':
                    newS.Append("\\n");
                    break;
                case '\t':
                    newS.Append("\\t");
                    break;
                case '\r':
                    newS.Append("\\r");
                    break;
                default:
                    newS.Append(c);
                    break;
            }
        }
        return newS.ToString();
    }

    private class PolyEvalType {
        public string typeStr;
        public string typeName;
        public PolyEvalType? valueType;
        public PolyEvalType? keyType;

        public PolyEvalType(string typeStr) {
            this.typeStr = typeStr;
            if (!typeStr.Contains("<")) {
                this.typeName = typeStr;
                return;
            }
            else {
                int idx = typeStr.IndexOf("<");
                this.typeName = typeStr.Substring(0, idx);
                string otherStr = typeStr.Substring(idx + 1, typeStr.Length - idx - 2);
                if (!otherStr.Contains(",")) {
                    this.valueType = new PolyEvalType(otherStr);
                }
                else {
                    idx = otherStr.IndexOf(",");
                    this.keyType = new PolyEvalType(otherStr.Substring(0, idx));
                    this.valueType = new PolyEvalType(otherStr.Substring(idx + 1));
                }
            }
        }
    }

    private static string GenVoid(object? value) {
        if (value != null) {
            throw new Exception("value is not null");
        }
        return "null";
    }

    private static string GenInt(object value) {
        if (!(value is int)) {
            throw new Exception("value is not int");
        }
        return value.ToString();
    }

    private static string GenLong(object value) {
        if (!(value is long)) {
            throw new Exception("value is not long");
        }
        return value.ToString() + "L";
    }

    private static string GenDouble(object value) {
        if (!(value is double)) {
            throw new Exception("value is not double");
        }
        double f = (double) value;
        if (double.IsNaN(f)) {
            return "nan";
        }
        else if (double.IsInfinity(f)) {
            if (f > 0) {
                return "inf";
            }
            else {
                return "-inf";
            }
        }
        string valueStr = string.Format("{0:N6}", f).TrimEnd('0');
        if (valueStr.EndsWith(".")) {
            valueStr += "0";
        }
        if (valueStr.Equals("-0.0")) {
            valueStr = "0.0";
        }
        return valueStr;
    }

    private static string GenBool(object value) {
        if (!(value is bool)) {
            throw new Exception("value is not bool");
        }
        return (bool) value ? "true" : "false";
    }

    private static string GenChar(object value) {
        if (!(value is char)) {
            throw new Exception("value is not char");
        }
        return "'" + EscapeString(value.ToString()) + "'";
    }

    private static string GenString(object value) {
        if (!(value is string)) {
            throw new Exception("value is not string");
        }
        return "\"" + EscapeString((string) value) + "\"";
    }

    private static string GenAny(object value) {
        if (value is bool) {
            return GenBool(value);
        }
        else if (value is int) {
            return GenInt(value);
        }
        else if (value is long) {
            return GenLong(value);
        }
        else if (value is double) {
            return GenDouble(value);
        }
        else if (value is char) {
            return GenChar(value);
        }
        else if (value is string) {
            return GenString(value);
        }
        throw new Exception("value is not any");
    }

    private static string GenList(object value, PolyEvalType t) {
        if (!(value is IList)) {
            throw new Exception("value is not IList");
        }
        IList list = (IList) value;
        List<string> vStrs = new List<string>();
        foreach (object v in list) {
            vStrs.Add(ToPolyEvalStrWithType(v, t.valueType));
        }
        string vStr = string.Join(", ", vStrs);
        return "[" + vStr + "]";

    }

    private static string GenMlist(object value, PolyEvalType t) {
        if (!(value is IList)) {
            throw new Exception("value is not IList");
        }
        IList list = (IList) value;
        List<string> vStrs = new List<string>();
        foreach (object v in list) {
            vStrs.Add(ToPolyEvalStrWithType(v, t.valueType));
        }
        string vStr = string.Join(", ", vStrs);
        return "[" + vStr + "]";
    }

    private static string GenUnorderedlist(object value, PolyEvalType t) {
        if (!(value is IList)) {
            throw new Exception("value is not IList");
        }
        IList list = (IList) value;
        List<string> vStrs = new List<string>();
        foreach (object v in list) {
            vStrs.Add(ToPolyEvalStrWithType(v, t.valueType));
        }
        vStrs.Sort();
        string vStr = string.Join(", ", vStrs);
        return "[" + vStr + "]";
    }

    private static string GenDict(object value, PolyEvalType t) {
        if (!(value is IDictionary)) {
            throw new Exception("value is not IDictionary");
        }
        IDictionary map = (IDictionary) value;
        List<string> vStrs = new List<string>();
        foreach (DictionaryEntry entry in map) {
            object key = entry.Key;
            object val = entry.Value;
            string kStr = ToPolyEvalStrWithType(key, t.keyType);
            string valStr = ToPolyEvalStrWithType(val, t.valueType);
            vStrs.Add(kStr + "=>" + valStr);
        }
        vStrs.Sort();
        string vStr = string.Join(", ", vStrs);
        return "{" + vStr + "}";
    }

    private static string GenMdict(object value, PolyEvalType t) {
        if (!(value is IDictionary)) {
            throw new Exception("value is not IDictionary");
        }
        IDictionary map = (IDictionary) value;
        List<string> vStrs = new List<string>();
        foreach (DictionaryEntry entry in map) {
            object key = entry.Key;
            object val = entry.Value;
            string kStr = ToPolyEvalStrWithType(key, t.keyType);
            string valStr = ToPolyEvalStrWithType(val, t.valueType);
            vStrs.Add(kStr + "=>" + valStr);
        }
        vStrs.Sort();
        string vStr = string.Join(", ", vStrs);
        return "{" + vStr + "}";
    }

    private static string GenOptional(object? value, PolyEvalType t) {
        if(value is null){
            return "null";
        }
        else {
            return ToPolyEvalStr(value, t.valueType);
        }
    }

    private static string ToPolyEvalStr(object? value, PolyEvalType t) {
        string typeName = t.typeName;
        if (typeName.Equals("void")) {
            return GenVoid(value);
        }
        else if (typeName.Equals("int")) {
            return GenInt(value);
        }
        else if (typeName.Equals("long")) {
            return GenLong(value);
        }
        else if (typeName.Equals("double")) {
            return GenDouble(value);
        }
        else if (typeName.Equals("bool")) {
            return GenBool(value);
        }
        else if (typeName.Equals("char")) {
            return GenChar(value);
        }
        else if (typeName.Equals("string")) {
            return GenString(value);
        }
        else if (typeName.Equals("any")) {
            return GenAny(value);
        }
        else if (typeName.Equals("list")) {
            return GenList(value, t);
        }
        else if (typeName.Equals("mlist")) {
            return GenMlist(value, t);
        }
        else if (typeName.Equals("unorderedlist")) {
            return GenUnorderedlist(value, t);
        }
        else if (typeName.Equals("dict")) {
            return GenDict(value, t);
        }
        else if (typeName.Equals("mdict")) {
            return GenMdict(value, t);
        }
        else if (typeName.Equals("optional")) {
            return GenOptional(value, t);
        }
        throw new Exception("unknown type");
    }

    private static string ToPolyEvalStrWithType(object? value, PolyEvalType t) {
        return ToPolyEvalStr(value, t) + ":" + t.typeStr;
    }

    public static string MyStringify(object? value, string typeStr) {
        return ToPolyEvalStrWithType(value, new PolyEvalType(typeStr));
    }
}

$$code$$