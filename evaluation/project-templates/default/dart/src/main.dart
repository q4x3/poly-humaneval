import 'dart:core';
import 'dart:math';
import 'dart:convert';
import 'dart:io';
import 'dart:collection';

class PolyEvalType {
    String typeStr = "";
    String typeName = "";
    PolyEvalType? valueType;
    PolyEvalType? keyType;

    PolyEvalType(String typeStr) {
        this.typeStr = typeStr;
        if (!typeStr.contains("<")) {
            this.typeName = typeStr;
        } else {
            int idx = typeStr.indexOf("<");
            this.typeName = typeStr.substring(0, idx);
            String otherStr = typeStr.substring(idx + 1, typeStr.length - 1);
            if (!otherStr.contains(",")) {
                this.valueType = new PolyEvalType(otherStr);
            } else {
                int idx = otherStr.indexOf(",");
                this.keyType = new PolyEvalType(otherStr.substring(0, idx));
                this.valueType = new PolyEvalType(otherStr.substring(idx + 1));
            }
        }
    }
}

class Utils {
    static String escapeString(String s) {
        StringBuffer newS = new StringBuffer();
        for (int i = 0; i < s.length; i++) {
            String c = s[i];
            switch (c) {
                case '\\':
                    newS.write("\\\\");
                    break;
                case '\"':
                    newS.write("\\\"");
                    break;
                case '\n':
                    newS.write("\\n");
                    break;
                case '\t':
                    newS.write("\\t");
                    break;
                case '\r':
                    newS.write("\\r");
                    break;
                default:
                    newS.write(c);
            }
        }
        return newS.toString();
    }

    static String genVoid(Object? value) {
        assert(value == null);
        return "null";
    }

    static String genInt(Object? value) {
        assert(value is int);
        return value.toString();
    }

    static String genLong(Object? value) {
        assert(value is int);
        return value.toString() + "L";
    }

    static String genDouble(Object? value) {
        assert(value is double);
        double f = value as double;
        if (f.isNaN) {
            return "nan";
        } else if (f.isInfinite) {
            if (f > 0) {
                return "inf";
            } else {
                return "-inf";
            }
        }
        String valueStr = f.toStringAsFixed(6);
        while (valueStr.endsWith("0")) {
            valueStr = valueStr.substring(0, valueStr.length - 1);
        }
        if (valueStr.endsWith(".")) {
            valueStr += "0";
        }
        if (valueStr == "-0.0") {
            valueStr = "0.0";
        }
        return valueStr;
    }

    static String genBool(Object? value) {
        assert(value is bool);
        return (value as bool) ? "true" : "false";
    }

    static String genChar(Object? value) {
        assert(value is String);
        return "'" + escapeString((value as String)) + "'";
    }

    static String genString(Object? value) {
        assert(value is String);
        return "\"" + escapeString(value as String) + "\"";
    }

    static String genAny(Object? value) {
        if (value is bool) {
            return genBool(value);
        } else if (value is int) {
            return genInt(value);
        } else if (value is double) {
            return genDouble(value);
        } else if (value is String) {
            return genString(value);
        }
        assert(false);
        return "";
    }

    static String genList(Object? value, PolyEvalType t) {
        assert(value is List);
        List list = value as List;
        List<String> vStrs = [];
        for (var v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!));
        }
        String vStr = vStrs.join(", ");
        return "[$vStr]";
    }

    static String genMlist(Object? value, PolyEvalType t) {
        assert(value is List);
        List list = value as List;
        List<String> vStrs = [];
        for (var v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!));
        }
        String vStr = vStrs.join(", ");
        return "[$vStr]";
    }

    static String genUnorderedlist(Object? value, PolyEvalType t) {
        assert(value is List);
        List list = value as List;
        List<String> vStrs = [];
        for (var v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!));
        }
        vStrs.sort();
        String vStr = vStrs.join(", ");
        return "[$vStr]";
    }

    static String genDict(Object? value, PolyEvalType t) {
        assert(value is Map);
        Map map = value as Map;
        List<String> vStrs = [];
        map.forEach((key, value) {
            String kStr = toPolyEvalStrWithType(key, t.keyType!);
            String vStr = toPolyEvalStrWithType(value, t.valueType!);
            vStrs.add("$kStr=>$vStr");
        });
        vStrs.sort();
        String vStr = vStrs.join(", ");
        return "{$vStr}";
    }

    static String genMdict(Object? value, PolyEvalType t) {
        assert(value is Map);
        Map map = value as Map;
        List<String> vStrs = [];
        map.forEach((key, value) {
            String kStr = toPolyEvalStrWithType(key, t.keyType!);
            String vStr = toPolyEvalStrWithType(value, t.valueType!);
            vStrs.add("$kStr=>$vStr");
        });
        vStrs.sort();
        String vStr = vStrs.join(", ");
        return "{$vStr}";
    }

    static String genOptional(Object? value, PolyEvalType t) {
        return value != null ? toPolyEvalStr(value, t.valueType!) : "null";
    }

    static String toPolyEvalStr(Object? value, PolyEvalType t) {
        String typeName = t.typeName;
        if (typeName == "void") {
            return genVoid(value);
        } else if (typeName == "int") {
            return genInt(value);
        } else if (typeName == "long") {
            return genLong(value);
        } else if (typeName == "double") {
            return genDouble(value);
        } else if (typeName == "bool") {
            return genBool(value);
        } else if (typeName == "char") {
            return genChar(value);
        } else if (typeName == "string") {
            return genString(value);
        } else if (typeName == "any") {
            return genAny(value);
        } else if (typeName == "list") {
            return genList(value, t);
        } else if (typeName == "mlist") {
            return genMlist(value, t);
        } else if (typeName == "unorderedlist") {
            return genUnorderedlist(value, t);
        } else if (typeName == "dict") {
            return genDict(value, t);
        } else if (typeName == "mdict") {
            return genMdict(value, t);
        } else if (typeName == "optional") {
            return genOptional(value, t);
        }
        assert(false);
        return "";
    }

    static String toPolyEvalStrWithType(Object? value, PolyEvalType t) {
        return toPolyEvalStr(value, t) + ":" + t.typeStr;
    }

    static String myStringify(Object? value, String typeStr) {
        return toPolyEvalStrWithType(value, new PolyEvalType(typeStr));
    }
}

var myStringify = Utils.myStringify;

$$code$$