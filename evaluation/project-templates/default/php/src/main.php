<?php

namespace utils {
    function escapeString($s) {
        $newS = [];
        for ($i = 0; $i < strlen($s); $i++) {
            $c = $s[$i];
            switch ($c) {
                case "\\":
                    $newS[] = "\\\\";
                    break;
                case "\"":
                    $newS[] = "\\\"";
                    break;
                case "\n":
                    $newS[] = "\\n";
                    break;
                case "\t":
                    $newS[] = "\\t";
                    break;
                case "\r":
                    $newS[] = "\\r";
                    break;
                default:
                    $newS[] = $c;
                    break;
            }
        }
        return implode("", $newS);
    }

    class PolyEvalType {
        public $typeStr;
        public $typeName;
        public $valueType;
        public $keyType;

        public function __construct($typeStr) {
            $this->typeStr = $typeStr;
            $this->typeName = "";
            $this->valueType = null;
            $this->keyType = null;
            if (!strpos($typeStr, "<")) {
                $this->typeName = $typeStr;
                return;
            }
            else {
                $idx = strpos($typeStr, "<");
                $this->typeName = substr($typeStr, 0, $idx);
                $otherStr = substr($typeStr, $idx + 1, strlen($typeStr) - $idx - 2);
                if (!strpos($otherStr, ",")) {
                    $this->valueType = new PolyEvalType($otherStr);
                }
                else {
                    $idx = strpos($otherStr, ",");
                    $this->keyType = new PolyEvalType(substr($otherStr, 0, $idx));
                    $this->valueType = new PolyEvalType(substr($otherStr, $idx + 1));
                }
            }
        }
    }

    function genVoid($value) {
        if ($value !== null) {
            throw new Exception("value is not null");
        }
        return "null";
    }

    function genInt($value) {
        if (is_null(filter_var($value, FILTER_VALIDATE_INT, FILTER_NULL_ON_FAILURE))) {
            throw new Exception("value is not number");
        }
        return strval($value);
    }

    function genLong($value) {
        if (is_null(filter_var($value, FILTER_VALIDATE_INT, FILTER_NULL_ON_FAILURE))) {
            throw new Exception("value is not number");
        }
        return strval($value) . "L";
    }

    function genDouble($value) {
        if (is_null(filter_var($value, FILTER_VALIDATE_FLOAT, FILTER_NULL_ON_FAILURE))) {
            throw new Exception("value is not number");
        }
        $f = floatval($value);
        if (is_nan($f)) {
            return "nan";
        }
        else if ($f === INF) {
            return "inf";
        }
        else if ($f === -INF) {
            return "-inf";
        }
        $valueStr = sprintf("%.6f", $f);
        while (substr($valueStr, -1) === "0") {
            $valueStr = substr($valueStr, 0, strlen($valueStr) - 1);
        }
        if (substr($valueStr, -1) === ".") {
            $valueStr .= "0";
        }
        if ($valueStr === "-0.0") {
            $valueStr = "0.0";
        }
        return $valueStr;
    }

    function genBool($value) {
        if (is_null(filter_var($value, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE))) {
            throw new Exception("value is not boolean");
        }
        return $value ? "true" : "false";
    }

    function genChar($value) {
        return "'" . escapeString($value) . "'";
    }

    function genString($value) {
        return "\"" . escapeString($value) . "\"";
    }

    function genAny($value) {
        if (is_bool($value)) {
            return genBool($value);
        }
        else if (is_int($value) || is_float($value)) {
            return genDouble($value);
        }
        else if (is_string($value)) {
            return genString($value);
        }
        throw new Exception("value is not any");
    }

    function genList($value, $t) {
        if (!is_array($value)) {
            throw new Exception("value is not array");
        }
        $vStrs = [];
        foreach ($value as $v) {
            $vStrs[] = toPolyEvalStrWithType($v, $t->valueType);
        }
        $vStr = implode(", ", $vStrs);
        return "[" . $vStr . "]";
    }

    function genMlist($value, $t) {
        if (!is_array($value)) {
            throw new Exception("value is not array");
        }
        $vStrs = [];
        foreach ($value as $v) {
            $vStrs[] = toPolyEvalStrWithType($v, $t->valueType);
        }
        $vStr = implode(", ", $vStrs);
        return "[" . $vStr . "]";
    }

    function genUnorderedlist($value, $t) {
        if (!is_array($value)) {
            throw new Exception("value is not array");
        }
        $vStrs = [];
        foreach ($value as $v) {
            $vStrs[] = toPolyEvalStrWithType($v, $t->valueType);
        }
        sort($vStrs);
        $vStr = implode(", ", $vStrs);
        return "[" . $vStr . "]";
    }

    function genDict($value, $t) {
        if (!is_array($value)) {
            throw new Exception("value is not array");
        }
        $vStrs = [];
        foreach ($value as $key => $val) {
            $kStr = toPolyEvalStrWithType($key, $t->keyType);
            $vStr = toPolyEvalStrWithType($val, $t->valueType);
            $vStrs[] = $kStr . "=>" . $vStr;
        }
        sort($vStrs);
        $vStr = implode(", ", $vStrs);
        return "{" . $vStr . "}";
    }

    function genMdict($value, $t) {
        if (!is_array($value)) {
            throw new Exception("value is not array");
        }
        $vStrs = [];
        foreach ($value as $key => $val) {
            $kStr = toPolyEvalStrWithType($key, $t->keyType);
            $vStr = toPolyEvalStrWithType($val, $t->valueType);
            $vStrs[] = $kStr . "=>" . $vStr;
        }
        sort($vStrs);
        $vStr = implode(", ", $vStrs);
        return "{" . $vStr . "}";
    }

    function genOptional($value, $t) {
        if ($value === null) {
            return "null";
        }
        else {
            return toPolyEvalStr($value, $t->valueType);
        }
    }

    function toPolyEvalStr($value, $t) {
        $typeName = $t->typeName;
        if ($typeName === "void") {
            return genVoid($value);
        }
        else if ($typeName === "int") {
            return genInt($value);
        }
        else if ($typeName === "long") {
            return genLong($value);
        }
        else if ($typeName === "double") {
            return genDouble($value);
        }
        else if ($typeName === "bool") {
            return genBool($value);
        }
        else if ($typeName === "char") {
            return genChar($value);
        }
        else if ($typeName === "string") {
            return genString($value);
        }
        else if ($typeName === "any") {
            return genAny($value);
        }
        else if ($typeName === "list") {
            return genList($value, $t);
        }
        else if ($typeName === "mlist") {
            return genMlist($value, $t);
        }
        else if ($typeName === "unorderedlist") {
            return genUnorderedlist($value, $t);
        }
        else if ($typeName === "dict") {
            return genDict($value, $t);
        }
        else if ($typeName === "mdict") {
            return genMdict($value, $t);
        }
        else if ($typeName === "optional") {
            return genOptional($value, $t);
        }
        throw new Exception("unknown type");
    }

    function toPolyEvalStrWithType($value, $t) {
        return toPolyEvalStr($value, $t) . ":" . $t->typeStr;
    }

    function myStringify($value, $typeStr) {
        return toPolyEvalStrWithType($value, new PolyEvalType($typeStr));
    }
}

namespace {
use function utils\myStringify as myStringify;

$$code$$

}