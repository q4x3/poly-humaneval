package src

import java.io.File
import kotlin.collections.*
import kotlin.math.*
import kotlin.text.Regex
import java.util.*
import java.security.*

object Utils {
    private fun escapeString(s: String): String {
        val newS = StringBuilder()
        for (i in 0 until s.length) {
            val c = s[i]
            when (c) {
                '\\' -> newS.append("\\\\")
                '\"' -> newS.append("\\\"")
                '\n' -> newS.append("\\n")
                '\t' -> newS.append("\\t")
                '\u000C' -> newS.append("\\f")
                else -> newS.append(c)
            }
        }
        return newS.toString()
    }

    private class PolyEvalType(typeStr: String) {
        var typeStr: String
        var typeName: String
        var valueType: PolyEvalType? = null
        var keyType: PolyEvalType? = null

        init {
            this.typeStr = typeStr
            if (!typeStr.contains("<")) {
                this.typeName = typeStr
            } else {
                val idx = typeStr.indexOf("<")
                this.typeName = typeStr.substring(0, idx)
                val otherStr = typeStr.substring(idx + 1, typeStr.length - 1)
                if (!otherStr.contains(",")) {
                    this.valueType = PolyEvalType(otherStr)
                } else {
                    val idx = otherStr.indexOf(",")
                    this.keyType = PolyEvalType(otherStr.substring(0, idx))
                    this.valueType = PolyEvalType(otherStr.substring(idx + 1))
                }
            }
        }
    }

    private fun genVoid(value: Any?): String {
        assert(value == null)
        return "null"
    }

    private fun genInt(value: Any?): String {
        assert(value is Int)
        return value.toString()
    }

    private fun genLong(value: Any?): String {
        assert(value is Long)
        return value.toString() + "L"
    }

    private fun genDouble(value: Any?): String {
        assert(value is Double)
        val f = value as Double
        if (f.isNaN()) {
            return "nan"
        } else if (f.isInfinite()) {
            if (f > 0) {
                return "inf"
            } else {
                return "-inf"
            }
        }
        var valueStr = String.format("%.6f", f).replace("0*$".toRegex(), "")
        if (valueStr.endsWith(".")) {
            valueStr += "0"
        }
        if (valueStr == "-0.0") {
            valueStr = "0.0"
        }
        return valueStr
    }

    private fun genBool(value: Any?): String {
        assert(value is Boolean)
        return if (value as Boolean) "true" else "false"
    }

    private fun genChar(value: Any?): String {
        assert(value is Char)
        return "'" + escapeString((value as Char).toString()) + "'"
    }

    private fun genString(value: Any?): String {
        assert(value is String)
        return "\"" + escapeString(value as String) + "\""
    }

    private fun genAny(value: Any?): String {
        if (value is Boolean) {
            return genBool(value)
        } else if (value is Int) {
            return genInt(value)
        } else if (value is Long) {
            return genLong(value)
        } else if (value is Double) {
            return genDouble(value)
        } else if (value is Char) {
            return genChar(value)
        } else if (value is String) {
            return genString(value)
        }
        assert(false)
        return ""
    }

    private fun genList(value: Any?, t: PolyEvalType): String {
        assert(value is List<*>)
        val list = value as List<*>
        val vStrs = ArrayList<String>()
        for (v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!!))
        }
        val vStr = vStrs.joinToString(", ")
        return "[$vStr]"
    }

    private fun genMlist(value: Any?, t: PolyEvalType): String {
        assert(value is List<*>)
        val list = value as List<*>
        val vStrs = ArrayList<String>()
        for (v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!!))
        }
        val vStr = vStrs.joinToString(", ")
        return "[$vStr]"
    }

    private fun genUnorderedlist(value: Any?, t: PolyEvalType): String {
        assert(value is List<*>)
        val list = value as List<*>
        val vStrs = ArrayList<String>()
        for (v in list) {
            vStrs.add(toPolyEvalStrWithType(v, t.valueType!!))
        }
        vStrs.sort()
        val vStr = vStrs.joinToString(", ")
        return "[$vStr]"
    }

    private fun genDict(value: Any?, t: PolyEvalType): String {
        assert(value is Map<*, *>)
        val map = value as Map<*, *>
        val vStrs = ArrayList<String>()
        map.forEach { (key, value) ->
            val kStr = toPolyEvalStrWithType(key, t.keyType!!)
            val vStr = toPolyEvalStrWithType(value, t.valueType!!)
            vStrs.add("$kStr=>$vStr")
        }
        vStrs.sort()
        val vStr = vStrs.joinToString(", ")
        return "{$vStr}"
    }

    private fun genMdict(value: Any?, t: PolyEvalType): String {
        assert(value is Map<*, *>)
        val map = value as Map<*, *>
        val vStrs = ArrayList<String>()
        map.forEach { (key, value) ->
            val kStr = toPolyEvalStrWithType(key, t.keyType!!)
            val vStr = toPolyEvalStrWithType(value, t.valueType!!)
            vStrs.add("$kStr=>$vStr")
        }
        vStrs.sort()
        val vStr = vStrs.joinToString(", ")
        return "{$vStr}"
    }

    private fun genOptional(value: Any?, t: PolyEvalType): String {
        return if (value != null) {
            toPolyEvalStr(value, t.valueType!!)
        } else {
            "null"
        }
    }

    private fun toPolyEvalStr(value: Any?, t: PolyEvalType): String {
        val typeName = t.typeName
        if (typeName == "void") {
            return genVoid(value)
        } else if (typeName == "int") {
            return genInt(value)
        } else if (typeName == "long") {
            return genLong(value)
        } else if (typeName == "double") {
            return genDouble(value)
        } else if (typeName == "bool") {
            return genBool(value)
        } else if (typeName == "char") {
            return genChar(value)
        } else if (typeName == "string") {
            return genString(value)
        } else if (typeName == "any") {
            return genAny(value)
        } else if (typeName == "list") {
            return genList(value, t)
        } else if (typeName == "mlist") {
            return genMlist(value, t)
        } else if (typeName == "unorderedlist") {
            return genUnorderedlist(value, t)
        } else if (typeName == "dict") {
            return genDict(value, t)
        } else if (typeName == "mdict") {
            return genMdict(value, t)
        } else if (typeName == "optional") {
            return genOptional(value, t)
        }
        assert(false)
        return ""
    }

    private fun toPolyEvalStrWithType(value: Any?, t: PolyEvalType): String {
        return toPolyEvalStr(value, t) + ":" + t.typeStr
    }

    public fun myStringify(value: Any?, typeStr: String): String {
        return toPolyEvalStrWithType(value, PolyEvalType(typeStr))
    }
}

val myStringify = Utils::myStringify

$$code$$