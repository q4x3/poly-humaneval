import Foundation

enum Utils {
    private static func escapeString(_ s: String) -> String {
        var newS = ""
        for c in s {
            switch c {
                case "\\": newS += "\\\\"
                case "\"": newS += "\\\""
                case "\n": newS += "\\n"
                case "\t": newS += "\\t"
                case "\r": newS += "\\r"
                default: newS += String(c)
            }
        }
        return newS
    }

    private class PolyEvalType {
        var typeStr = ""
        var typeName = ""
        var valueType: PolyEvalType?
        var keyType: PolyEvalType?

        init(_ typeStr: String) {
            self.typeStr = typeStr
            if !typeStr.contains("<") {
                self.typeName = typeStr
            } else {
                let idx = typeStr.firstIndex(of: "<")!
                self.typeName = String(typeStr[..<idx])
                let otherStr = String(typeStr[typeStr.index(after: idx)..<typeStr.index(before: typeStr.endIndex)])
                if !otherStr.contains(",") {
                    self.valueType = PolyEvalType(otherStr)
                } else {
                    let idx = otherStr.firstIndex(of: ",")!
                    self.keyType = PolyEvalType(String(otherStr[..<idx]))
                    self.valueType = PolyEvalType(String(otherStr[otherStr.index(after: idx)...]))
                }
            }
        }
    }

    private static func genVoid(_ value: Any?) -> String {
        assert(value == nil)
        return "nil"
    }

    private static func genInt(_ value: Any?) -> String {
        assert(value is Int)
        return String(describing: value!)
    }

    private static func genLong(_ value: Any?) -> String {
        assert(value is Int64)
        return String(describing: value!) + "L"
    }

    private static func genDouble(_ value: Any?) -> String {
        assert(value is Double)
        let f = value as! Double
        if f.isNaN {
            return "nan"
        } else if f.isInfinite {
            if f > 0 {
                return "inf"
            } else {
                return "-inf"
            }
        }
        var valueStr = String(format: "%.6f", f)
        while valueStr.hasSuffix("0") {
            valueStr = String(valueStr[..<valueStr.index(before: valueStr.endIndex)])
        }
        if valueStr.hasSuffix(".") {
            valueStr += "0"
        }
        if valueStr == "-0.0" {
            valueStr = "0.0"
        }
        return valueStr
    }

    private static func genBool(_ value: Any?) -> String {
        assert(value is Bool)
        return (value as! Bool) ? "true" : "false"
    }

    private static func genChar(_ value: Any?) -> String {
        assert(value is String)
        return "'" + escapeString(value as! String) + "'"
    }

    private static func genString(_ value: Any?) -> String {
        assert(value is String)
        return "\"" + escapeString(value as! String) + "\""
    }

    private static func genAny(_ value: Any?) -> String {
        if value is Bool {
            return genBool(value)
        } else if value is Int {
            return genInt(value)
        } else if value is Double {
            return genDouble(value)
        } else if value is String {
            return genString(value)
        }
        assert(false)
        return ""
    }

    private static func genList(_ value: Any?, _ t: PolyEvalType) -> String {
        assert(value is [Any?])
        let list = value as! [Any?]
        var vStrs = [String]()
        for v in list {
            vStrs.append(toPolyEvalStrWithType(v, t.valueType!))
        }
        let vStr = vStrs.joined(separator: ", ")
        return "[\(vStr)]"
    }

    private static func genMlist(_ value: Any?, _ t: PolyEvalType) -> String {
        assert(value is [Any?])
        let list = value as! [Any?]
        var vStrs = [String]()
        for v in list {
            vStrs.append(toPolyEvalStrWithType(v, t.valueType!))
        }
        let vStr = vStrs.joined(separator: ", ")
        return "[\(vStr)]"
    }

    private static func genUnorderedlist(_ value: Any?, _ t: PolyEvalType) -> String {
        assert(value is [Any?])
        let list = value as! [Any?]
        var vStrs = [String]()
        for v in list {
            vStrs.append(toPolyEvalStrWithType(v, t.valueType!))
        }
        vStrs.sort()
        let vStr = vStrs.joined(separator: ", ")
        return "[\(vStr)]"
    }

    private static func genDict(_ value: Any?, _ t: PolyEvalType) -> String {
        assert(value is [AnyHashable: Any?])
        let map = value as! [AnyHashable: Any?]
        var vStrs = [String]()
        for (key, value) in map {
            let kStr = toPolyEvalStrWithType(key, t.keyType!)
            let vStr = toPolyEvalStrWithType(value, t.valueType!)
            vStrs.append("\(kStr):\(vStr)")
        }
        vStrs.sort()
        let vStr = vStrs.joined(separator: ", ")
        return "{\(vStr)}"
    }

    private static func genMdict(_ value: Any?, _ t: PolyEvalType) -> String {
        assert(value is [AnyHashable: Any?])
        let map = value as! [AnyHashable: Any?]
        var vStrs = [String]()
        for (key, value) in map {
            let kStr = toPolyEvalStrWithType(key, t.keyType!)
            let vStr = toPolyEvalStrWithType(value, t.valueType!)
            vStrs.append("\(kStr):\(vStr)")
        }
        vStrs.sort()
        let vStr = vStrs.joined(separator: ", ")
        return "{\(vStr)}"
    }

    private static func genOptional(_ value: Any?, _ t: PolyEvalType) -> String {
        return value != nil ? toPolyEvalStr(value, t.valueType!) : "nil"
    }

    private static func toPolyEvalStr(_ value: Any?, _ t: PolyEvalType) -> String {
        let typeName = t.typeName
        if typeName == "void" {
            return genVoid(value)
        } else if typeName == "int" {
            return genInt(value)
        } else if typeName == "long" {
            return genLong(value)
        } else if typeName == "double" {
            return genDouble(value)
        } else if typeName == "bool" {
            return genBool(value)
        } else if typeName == "char" {
            return genChar(value)
        } else if typeName == "string" {
            return genString(value)
        } else if typeName == "any" {
            return genAny(value)
        } else if typeName == "list" {
            return genList(value, t)
        } else if typeName == "mlist" {
            return genMlist(value, t)
        } else if typeName == "unorderedlist" {
            return genUnorderedlist(value, t)
        } else if typeName == "dict" {
            return genDict(value, t)
        } else if typeName == "mdict" {
            return genMdict(value, t)
        } else if typeName == "optional" {
            return genOptional(value, t)
        }
        assert(false)
        return ""
    }

    private static func toPolyEvalStrWithType(_ value: Any?, _ t: PolyEvalType) -> String {
        return toPolyEvalStr(value, t) + ":" + t.typeStr
    }

    static func myStringify(_ value: Any?, _ typeStr: String) -> String {
        return toPolyEvalStrWithType(value, PolyEvalType(typeStr))
    }
}