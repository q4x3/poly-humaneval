const escapeString = (s) => {
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
class PolyEvalType {
    public typeStr: string;
    public typeName: string;
    public valueType: PolyEvalType | null;
    public keyType: PolyEvalType | null;
    
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

const genVoid = (value) => {
    if (value !== null) {
        throw new Error("value is not null");
    }
    return "null";
}

const genInt = (value) => {
    if (!(typeof value === "number")) {
        throw new Error("value is not number");
    }
    return value.toString();
}

const genLong = (value) => {
    if (!(typeof value === "number")) {
        throw new Error("value is not number");
    }
    return value.toString() + "L";
}

const genDouble = (value) => {
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

const genBool = (value) => {
    if (!(typeof value === "boolean")) {
        throw new Error("value is not boolean");
    }
    return value ? "true" : "false";
}

const genChar = (value) => {
    if (!(typeof value === "string")) {
        throw new Error("value is not string");
    }
    return "'" + escapeString(value) + "'";
}

const genString = (value) => {
    if (!(typeof value === "string")) {
        throw new Error("value is not string");
    }
    return "\"" + escapeString(value) + "\"";
}

const genAny = (value) => {
    if (typeof value === "boolean") {
        return genBool(value);
    }
    else if (typeof value === "number") {
        return genInt(value);
    }
    else if (typeof value === "string") {
        return genString(value);
    }
    throw new Error("value is not any");
}

const genList = (value, t) => {
    if (!Array.isArray(value)) {
        throw new Error("value is not array");
    }
    let vStrs = [];
    for (let v of value) {
        vStrs.push(toPolyEvalStrWithType(v, t.valueType));
    }
    let vStr = vStrs.join(", ");
    return "[" + vStr + "]";
}

const genMlist = (value, t) => {
    if (!Array.isArray(value)) {
        throw new Error("value is not array");
    }
    let vStrs = [];
    for (let v of value) {
        vStrs.push(toPolyEvalStrWithType(v, t.valueType));
    }
    let vStr = vStrs.join(", ");
    return "[" + vStr + "]";
}

const genUnorderedlist = (value, t) => {
    if (!Array.isArray(value)) {
        throw new Error("value is not array");
    }
    let vStrs = [];
    for (let v of value) {
        vStrs.push(toPolyEvalStrWithType(v, t.valueType));
    }
    vStrs.sort();
    let vStr = vStrs.join(", ");
    return "[" + vStr + "]";
}

const genDict = (value, t) => {
    if (!(typeof value === "object")) {
        throw new Error("value is not object");
    }
    let vStrs = [];
    for (let key in value) {
        let val = value[key];
        let kStr = toPolyEvalStrWithType(key, t.keyType);
        let vStr = toPolyEvalStrWithType(val, t.valueType);
        vStrs.push(kStr + "=>" + vStr);
    }
    vStrs.sort();
    let vStr = vStrs.join(", ");
    return "{" + vStr + "}";
}

const genMdict = (value, t) => {
    if (!(typeof value === "object")) {
        throw new Error("value is not object");
    }
    let vStrs = [];
    for (let key in value) {
        let val = value[key];
        let kStr = toPolyEvalStrWithType(key, t.keyType);
        let vStr = toPolyEvalStrWithType(val, t.valueType);
        vStrs.push(kStr + "=>" + vStr);
    }
    vStrs.sort();
    let vStr = vStrs.join(", ");
    return "{" + vStr + "}";
}

const genOptional = (value, t) => {
    if (value === null) {
        return "null";
    }
    else {
        return toPolyEvalStr(value, t.valueType);
    }
}

const toPolyEvalStr = (value, t) => {
    let typeName = t.typeName;
    if (typeName === "void") {
        return genVoid(value);
    }
    else if (typeName === "int") {
        return genInt(value);
    }
    else if (typeName === "long") {
        return genLong(value);
    }
    else if (typeName === "double") {
        return genDouble(value);
    }
    else if (typeName === "bool") {
        return genBool(value);
    }
    else if (typeName === "char") {
        return genChar(value);
    }
    else if (typeName === "string") {
        return genString(value);
    }
    else if (typeName === "any") {
        return genAny(value);
    }
    else if (typeName === "list") {
        return genList(value, t);
    }
    else if (typeName === "mlist") {
        return genMlist(value, t);
    }
    else if (typeName === "unorderedlist") {
        return genUnorderedlist(value, t);
    }
    else if (typeName === "dict") {
        return genDict(value, t);
    }
    else if (typeName === "mdict") {
        return genMdict(value, t);
    }
    else if (typeName === "optional") {
        return genOptional(value, t);
    }
    throw new Error("unknown type");
}

const toPolyEvalStrWithType = (value, t) => {
    return toPolyEvalStr(value, t) + ":" + t.typeStr;
}

export const myStringify = (value, typeStr) => {
    return toPolyEvalStrWithType(value, new PolyEvalType(typeStr));
}