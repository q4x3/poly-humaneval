import fs from "fs";
import * as crypto from 'crypto';

class PolyEvalType {
    constructor(typeStr) {
        this.typeStr = typeStr;
        this.typeName = "";
        this.valueType = null;
        this.keyType = null;
        if (!typeStr.includes("<")) {
            this.typeName = typeStr;
            return;
        }
        else {
            let idx = typeStr.indexOf("<");
            this.typeName = typeStr.substring(0, idx);
            let otherStr = typeStr.substring(idx + 1, typeStr.length - 1);
            if (!otherStr.includes(",")) {
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

class Utils {
    static escapeString (s) {
        let newS = [];
        for (let i = 0; i < s.length; i++) {
            let c = s[i];
            switch (c) {
                case '\\':
                    newS.push("\\\\");
                    break;
                case '\"':
                    newS.push("\\\"");
                    break;
                case '\n':
                    newS.push("\\n");
                    break;
                case '\t':
                    newS.push("\\t");
                    break;
                case '\r':
                    newS.push("\\r");
                    break;
                default:
                    newS.push(c);
                    break;
            }
        }
        return newS.join("");
    }

    static genVoid(value) {
        if (value !== null) {
            throw new Error("value is not null");
        }
        return "null";
    }

    static genInt(value) {
        if (!(typeof value === "number")) {
            throw new Error("value is not number");
        }
        return value.toString();
    }

    static genLong(value) {
        if (!(typeof value === "number")) {
            throw new Error("value is not number");
        }
        return value.toString() + "L";
    }

    static genDouble(value) {
        if (!(typeof value === "number")) {
            throw new Error("value is not number");
        }
        let f = value;
        if (isNaN(f)) {
            return "nan";
        }
        else if (f === Number.POSITIVE_INFINITY) {
            return "inf";
        }
        else if (f === Number.NEGATIVE_INFINITY) {
            return "-inf";
        }
        let valueStr = f.toFixed(6)
        while (valueStr.endsWith("0")) {
            valueStr = valueStr.substring(0, valueStr.length - 1);
        }
        if (valueStr.endsWith(".")) {
            valueStr += "0";
        }
        if (valueStr === "-0.0") {
            valueStr = "0.0";
        }
        return valueStr;
    }

    static genBool(value) {
        if (!(typeof value === "boolean")) {
            throw new Error("value is not boolean");
        }
        return value ? "true" : "false";
    }

    static genChar(value) {
        if (!(typeof value === "string")) {
            throw new Error("value is not string");
        }
        return "'" + Utils.escapeString(value) + "'";
    }

    static genString(value) {
        if (!(typeof value === "string")) {
            throw new Error("value is not string");
        }
        return "\"" + Utils.escapeString(value) + "\"";
    }

    static genAny(value) {
        if (typeof value === "boolean") {
            return Utils.genBool(value);
        }
        else if (typeof value === "number") {
            return Utils.genInt(value);
        }
        else if (typeof value === "string") {
            return Utils.genString(value);
        }
        throw new Error("value is not any");
    }

    static genList(value, t) {
        if (!Array.isArray(value)) {
            throw new Error("value is not array");
        }
        let vStrs = [];
        for (let v of value) {
            vStrs.push(Utils.toPolyEvalStrWithType(v, t.valueType));
        }
        let vStr = vStrs.join(", ");
        return "[" + vStr + "]";
    }

    static genMlist(value, t) {
        if (!Array.isArray(value)) {
            throw new Error("value is not array");
        }
        let vStrs = [];
        for (let v of value) {
            vStrs.push(Utils.toPolyEvalStrWithType(v, t.valueType));
        }
        let vStr = vStrs.join(", ");
        return "[" + vStr + "]";
    }

    static genUnorderedlist(value, t) {
        if (!Array.isArray(value)) {
            throw new Error("value is not array");
        }
        let vStrs = [];
        for (let v of value) {
            vStrs.push(Utils.toPolyEvalStrWithType(v, t.valueType));
        }
        vStrs.sort();
        let vStr = vStrs.join(", ");
        return "[" + vStr + "]";
    }

    static genDict(value, t) {
        if (!(typeof value === "object")) {
            throw new Error("value is not object");
        }
        let vStrs = [];
        for (let key in value) {
            let val = value[key];
            let kStr = Utils.toPolyEvalStrWithType(key, t.keyType);
            let vStr = Utils.toPolyEvalStrWithType(val, t.valueType);
            vStrs.push(kStr + "=>" + vStr);
        }
        vStrs.sort();
        let vStr = vStrs.join(", ");
        return "{" + vStr + "}";
    }

    static genMdict(value, t) {
        if (!(typeof value === "object")) {
            throw new Error("value is not object");
        }
        let vStrs = [];
        for (let key in value) {
            let val = value[key];
            let kStr = Utils.toPolyEvalStrWithType(key, t.keyType);
            let vStr = Utils.toPolyEvalStrWithType(val, t.valueType);
            vStrs.push(kStr + "=>" + vStr);
        }
        vStrs.sort();
        let vStr = vStrs.join(", ");
        return "{" + vStr + "}";
    }

    static genOptional(value, t) {
        if (value === null) {
            return "null";
        }
        else {
            return Utils.toPolyEvalStr(value, t.valueType);
        }
    }

    static toPolyEvalStr(value, t) {
        let typeName = t.typeName;
        if (typeName === "void") {
            return Utils.genVoid(value);
        }
        else if (typeName === "int") {
            return Utils.genInt(value);
        }
        else if (typeName === "long") {
            return Utils.genLong(value);
        }
        else if (typeName === "double") {
            return Utils.genDouble(value);
        }
        else if (typeName === "bool") {
            return Utils.genBool(value);
        }
        else if (typeName === "char") {
            return Utils.genChar(value);
        }
        else if (typeName === "string") {
            return Utils.genString(value);
        }
        else if (typeName === "any") {
            return Utils.genAny(value);
        }
        else if (typeName === "list") {
            return Utils.genList(value, t);
        }
        else if (typeName === "mlist") {
            return Utils.genMlist(value, t);
        }
        else if (typeName === "unorderedlist") {
            return Utils.genUnorderedlist(value, t);
        }
        else if (typeName === "dict") {
            return Utils.genDict(value, t);
        }
        else if (typeName === "mdict") {
            return Utils.genMdict(value, t);
        }
        else if (typeName === "optional") {
            return Utils.genOptional(value, t);
        }
        throw new Error("unknown type");
    }

    static toPolyEvalStrWithType(value, t) {
        return Utils.toPolyEvalStr(value, t) + ":" + t.typeStr;
    }

    static myStringify(value, typeStr) {
        return Utils.toPolyEvalStrWithType(value, new PolyEvalType(typeStr));
    }
}

const myStringify = Utils.myStringify;

$$code$$