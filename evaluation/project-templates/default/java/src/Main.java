package src;

import java.lang.*;
import java.util.*;
import java.util.stream.*;
import java.util.regex.*;
import java.security.*;
import java.io.FileWriter;

import static src.Utils.myStringify;
import static src.Global.*;

class Utils {
    private static String escapeString(String s) {
        StringBuilder newS = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch(c) {
                case '\\':
                    newS.append("\\\\");
                    break;
                case '\"':
                    newS.append("\\\"");
                    break;
                case '\n':
                    newS.append("\\n");
                    break;
                case '\t':
                    newS.append("\\t");
                    break;
                case '\r':
                    newS.append("\\r");
                    break;
                default:
                    newS.append(c);
                    break;
            }
        }
        return newS.toString();
    }

    private static class PolyEvalType {
        public String typeStr;
        public String typeName;
        public PolyEvalType valueType;
        public PolyEvalType keyType;

        public PolyEvalType(String typeStr) {
            this.typeStr = typeStr;
            if (!typeStr.contains("<")) {
                this.typeName = typeStr;
                return;
            }
            else {
                int idx = typeStr.indexOf("<");
                this.typeName = typeStr.substring(0, idx);
                String otherStr = typeStr.substring(idx + 1, typeStr.length() - 1);
                if (!otherStr.contains(",")) {
                    this.valueType = new PolyEvalType(otherStr);
                }
                else {
                    idx = otherStr.indexOf(",");
                    this.keyType = new PolyEvalType(otherStr.substring(0, idx));
                    this.valueType = new PolyEvalType(otherStr.substring(idx + 1));
                }
            }
        }
    }

    private static String genVoid(Object value) {
        assert value == null;
        return "null";
    }

    private static String genInt(Object value) {
        assert value instanceof Integer;
        return value.toString();
    }

    private static String genLong(Object value) {
        assert value instanceof Long;
        return value.toString() + "L";
    }

    private static String genDouble(Object value) {
        assert value instanceof Double;
        double f = (double) value;
        if (Double.isNaN(f)) {
            return "nan";
        }
        else if (Double.isInfinite(f)) {
            if (f > 0) {
                return "inf";
            }
            else {
                return "-inf";
            }
        }
        String valueStr = String.format("%.6f", f).replaceAll("0*$", "");
        if (valueStr.endsWith(".")) {
            valueStr += "0";
        }
        if (valueStr.equals("-0.0")) {
            valueStr = "0.0";
        }
        return valueStr;
    }

    private static String genBool(Object value) {
        assert value instanceof Boolean;
        return (Boolean) value ? "true" : "false";
    }

    private static String genChar(Object value) {
        assert value instanceof Character;
        return "'" + escapeString(Character.toString((Character)value)) + "'";
    }

    private static String genString(Object value) {
        assert value instanceof String;
        return "\"" + escapeString((String) value) + "\"";
    }

    private static String genAny(Object value) {
        if (value instanceof Boolean) {
            return genBool(value);
        }
        else if (value instanceof Integer) {
            return genInt(value);
        }
        else if (value instanceof Long) {
            return genLong(value);
        }
        else if (value instanceof Double) {
            return genDouble(value);
        }
        else if (value instanceof Character) {
            return genChar(value);
        }
        else if (value instanceof String) {
            return genString(value);
        }
        assert false;
        return null;
    }

    private static String genList(Object value, PolyEvalType t) {
        assert value instanceof List;
        List<Object> list = (List<Object>) value;
        List<String> vStrs = new ArrayList<>();
        for (Object v : list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType));
        }
        String vStr = String.join(", ", vStrs);
        return "[" + vStr + "]";
    }

    private static String genMlist(Object value, PolyEvalType t) {
        assert value instanceof List;
        List<Object> list = (List<Object>) value;
        List<String> vStrs = new ArrayList<>();
        for (Object v : list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType));
        }
        String vStr = String.join(", ", vStrs);
        return "[" + vStr + "]";
    }

    private static String genUnorderedlist(Object value, PolyEvalType t) {
        assert value instanceof List;
        List<Object> list = (List<Object>) value;
        List<String> vStrs = new ArrayList<>();
        for (Object v : list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType));
        }
        Collections.sort(vStrs);
        String vStr = String.join(", ", vStrs);
        return "[" + vStr + "]";
    }

    private static String genDict(Object value, PolyEvalType t) {
        assert value instanceof Map;
        Map<Object, Object> map = (Map<Object, Object>) value;
        List<String> vStrs = new ArrayList<>();
        for (Map.Entry<Object, Object> entry : map.entrySet()) {
            Object key = entry.getKey();
            Object val = entry.getValue();
            String kStr = toPolyEvalStrWithType(key, t.keyType);
            String vStr = toPolyEvalStrWithType(val, t.valueType);
            vStrs.add(kStr + "=>" + vStr);
        }
        Collections.sort(vStrs);
        String vStr = String.join(", ", vStrs);
        return "{" + vStr + "}";
    }

    private static String genMdict(Object value, PolyEvalType t) {
        assert value instanceof Map;
        Map<Object, Object> map = (Map<Object, Object>) value;
        List<String> vStrs = new ArrayList<>();
        for (Map.Entry<Object, Object> entry : map.entrySet()) {
            Object key = entry.getKey();
            Object val = entry.getValue();
            String kStr = toPolyEvalStrWithType(key, t.keyType);
            String vStr = toPolyEvalStrWithType(val, t.valueType);
            vStrs.add(kStr + "=>" + vStr);
        }
        Collections.sort(vStrs);
        String vStr = String.join(", ", vStrs);
        return "{" + vStr + "}";
    }

    private static String genOptional(Object value, PolyEvalType t) {
        assert value instanceof Optional;
        Optional<Object> optValue = (Optional<Object>) value;
        if (optValue.isPresent()) {
            return toPolyEvalStr(optValue.get(), t.valueType);
        }
        else {
            return "null";
        }
    }

    private static String toPolyEvalStr(Object value, PolyEvalType t) {
        String typeName = t.typeName;
        if (typeName.equals("void")) {
            return genVoid(value);
        }
        else if (typeName.equals("int")) {
            return genInt(value);
        }
        else if (typeName.equals("long")) {
            return genLong(value);
        }
        else if (typeName.equals("double")) {
            return genDouble(value);
        }
        else if (typeName.equals("bool")) {
            return genBool(value);
        }
        else if (typeName.equals("char")) {
            return genChar(value);
        }
        else if (typeName.equals("string")) {
            return genString(value);
        }
        else if (typeName.equals("any")) {
            return genAny(value);
        }
        else if (typeName.equals("list")) {
            return genList(value, t);
        }
        else if (typeName.equals("mlist")) {
            return genMlist(value, t);
        }
        else if (typeName.equals("unorderedlist")) {
            return genUnorderedlist(value, t);
        }
        else if (typeName.equals("dict")) {
            return genDict(value, t);
        }
        else if (typeName.equals("mdict")) {
            return genMdict(value, t);
        }
        else if (typeName.equals("optional")) {
            return genOptional(value, t);
        }
        assert false;
        return null;
    }

    private static String toPolyEvalStrWithType(Object value, PolyEvalType t) {
        return toPolyEvalStr(value, t) + ":" + t.typeStr;
    }

    public static String myStringify(Object value, String typeStr) {
        return toPolyEvalStrWithType(value, new PolyEvalType(typeStr));
    }
}

$$code$$