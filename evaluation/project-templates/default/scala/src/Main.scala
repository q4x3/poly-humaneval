package src

import java.io.FileWriter
import scala.collection
import scala.collection.mutable
import scala.annotation.tailrec
import scala.collection.mutable
import scala.collection.mutable.{ListBuffer, HashMap}
import scala.math._
import scala.util.matching.Regex
import java.security._

object Utils {
    private def escapeString(s: String): String = {
        val newS = new StringBuilder()
        for (i <- 0 until s.length) {
            val c = s.charAt(i)
            c match {
                case '\\' => newS.append("\\\\")
                case '\"' => newS.append("\\\"")
                case '\n' => newS.append("\\n")
                case '\t' => newS.append("\\t")
                case '\r' => newS.append("\\r")
                case _ => newS.append(c)
            }
        }
        newS.toString()
    }

    class PolyEvalType(var typeStr: String) {
        var typeName: String = ""
        var valueType: PolyEvalType = _
        var keyType: PolyEvalType = _

        {
            if (!typeStr.contains("<")) {
                this.typeName = typeStr
            } else {
                val idx = typeStr.indexOf("<")
                this.typeName = typeStr.substring(0, idx)
                val otherStr = typeStr.substring(idx + 1, typeStr.length - 1)
                if (!otherStr.contains(",")) {
                    this.valueType = new PolyEvalType(otherStr)
                } else {
                    val idx = otherStr.indexOf(",")
                    this.keyType = new PolyEvalType(otherStr.substring(0, idx))
                    this.valueType = new PolyEvalType(otherStr.substring(idx + 1))
                }
            }
        }
    }

    private def genVoid(value: Any): String = {
        assert(value == null)
        "null"
    }

    private def genInt(value: Any): String = {
        assert(value.isInstanceOf[Int])
        value.toString
    }

    private def genLong(value: Any): String = {
        assert(value.isInstanceOf[Long])
        value.toString + "L"
    }

    private def genDouble(value: Any): String = {
        assert(value.isInstanceOf[Double])
        val f = value.asInstanceOf[Double]
        if (f.isNaN) {
            "nan"
        } else if (f.isInfinite) {
            if (f > 0) {
                "inf"
            } else {
                "-inf"
            }
        } else {
            var valueStr = "%.6f".format(f)
            while (valueStr.endsWith("0")) {
                valueStr = valueStr.substring(0, valueStr.length - 1)
            }
            if (valueStr.endsWith(".")) {
                valueStr += "0"
            }
            if (valueStr == "-0.0") {
                valueStr = "0.0"
            }
            valueStr
        }
    }

    private def genBool(value: Any): String = {
        assert(value.isInstanceOf[Boolean])
        if (value.asInstanceOf[Boolean]) "true" else "false"
    }

    private def genChar(value: Any): String = {
        assert(value.isInstanceOf[Char])
        "'" + escapeString(value.asInstanceOf[Char].toString) + "'"
    }

    private def genString(value: Any): String = {
        assert(value.isInstanceOf[String])
        "\"" + escapeString(value.asInstanceOf[String]) + "\""
    }

    private def genAny(value: Any): String = {
        if (value.isInstanceOf[Boolean]) {
            genBool(value)
        } else if (value.isInstanceOf[Int]) {
            genInt(value)
        } else if (value.isInstanceOf[Long]) {
            genLong(value)
        } else if (value.isInstanceOf[Double]) {
            genDouble(value)
        } else if (value.isInstanceOf[Char]) {
            genChar(value)
        } else if (value.isInstanceOf[String]) {
            genString(value)
        } else {
            assert(false)
            ""
        }
    }

    private def genList(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[collection.Seq[_]])
        val list = value.asInstanceOf[collection.Seq[_]]
        val vStrs = mutable.ListBuffer[String]()
        for (v <- list) {
            vStrs += toPolyEvalStrWithType(v, t.valueType)
        }
        val vStr = vStrs.mkString(", ")
        s"[$vStr]"
    }

    private def genMlist(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[mutable.Seq[_]])
        val list = value.asInstanceOf[mutable.Seq[_]]
        val vStrs = mutable.ListBuffer[String]()
        for (v <- list) {
            vStrs += toPolyEvalStrWithType(v, t.valueType)
        }
        val vStr = vStrs.mkString(", ")
        s"[$vStr]"
    }

    private def genUnorderedlist(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[collection.Seq[_]])
        val list = value.asInstanceOf[collection.Seq[_]]
        val vStrs = mutable.ListBuffer[String]()
        for (v <- list) {
            vStrs += toPolyEvalStrWithType(v, t.valueType)
        }
        val vStr = vStrs.sorted.mkString(", ")
        s"[$vStr]"
    }

    private def genDict(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[collection.Map[_, _]])
        val map = value.asInstanceOf[collection.Map[_, _]]
        val vStrs = mutable.ListBuffer[String]()
        map.foreach { case (key, value) =>
            val kStr = toPolyEvalStrWithType(key, t.keyType)
            val vStr = toPolyEvalStrWithType(value, t.valueType)
            vStrs += s"$kStr=>$vStr"
        }
        val vStr = vStrs.sorted.mkString(", ")
        s"{$vStr}"
    }

    private def genMdict(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[mutable.Map[_, _]])
        val map = value.asInstanceOf[mutable.Map[_, _]]
        val vStrs = mutable.ListBuffer[String]()
        map.foreach { case (key, value) =>
            val kStr = toPolyEvalStrWithType(key, t.keyType)
            val vStr = toPolyEvalStrWithType(value, t.valueType)
            vStrs += s"$kStr=>$vStr"
        }
        val vStr = vStrs.sorted.mkString(", ")
        s"{$vStr}"
    }

    private def genOptional(value: Any, t: PolyEvalType): String = {
        assert(value.isInstanceOf[Option[_]])
        val optValue = value.asInstanceOf[Option[_]]
        if (optValue.isDefined) {
            toPolyEvalStr(optValue.get, t.valueType)
        } else {
            "null"
        }
    }

    private def toPolyEvalStr(value: Any, t: PolyEvalType): String = {
        val typeName = t.typeName
        if (typeName == "void") {
            genVoid(value)
        } else if (typeName == "int") {
            genInt(value)
        } else if (typeName == "long") {
            genLong(value)
        } else if (typeName == "double") {
            genDouble(value)
        } else if (typeName == "bool") {
            genBool(value)
        } else if (typeName == "char") {
            genChar(value)
        } else if (typeName == "string") {
            genString(value)
        } else if (typeName == "any") {
            genAny(value)
        } else if (typeName == "list") {
            genList(value, t)
        } else if (typeName == "mlist") {
            genMlist(value, t)
        } else if (typeName == "unorderedlist") {
            genUnorderedlist(value, t)
        } else if (typeName == "dict") {
            genDict(value, t)
        } else if (typeName == "mdict") {
            genMdict(value, t)
        } else if (typeName == "optional") {
            genOptional(value, t)
        } else {
            assert(false)
            ""
        }
    }

    private def toPolyEvalStrWithType(value: Any, t: PolyEvalType): String = {
        toPolyEvalStr(value, t) + ":" + t.typeStr
    }

    def myStringify(value: Any, typeStr: String): String = {
        toPolyEvalStrWithType(value, new PolyEvalType(typeStr))
    }
}

def myStringify = Utils.myStringify

$$code$$