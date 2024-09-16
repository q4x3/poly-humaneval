package main

import (
    "os"
    "fmt"
    "math"
    "sort"
    "strconv"
    "strings"
    "unicode"
    "reflect"
    "regexp"
    "encoding/hex"
    "crypto/md5"
)

var _0 = fmt.Println
var _1 = math.Abs
var _2 = sort.Search
var _3 = strconv.FormatInt
var _4 = strings.Contains
var _5 = unicode.IsDigit
var _6 = reflect.TypeOf
var _7 = regexp.MustCompile
var _8 = hex.EncodeToString
var _9 = md5.Sum

func escapeString(s string) string {
    var newS strings.Builder
    for _, c := range s {
        switch c {
        case '\\':
            newS.WriteString("\\\\")
        case '"':
            newS.WriteString("\\\"")
        case '\n':
            newS.WriteString("\\n")
        case '\t':
            newS.WriteString("\\t")
        case '\u000C':
            newS.WriteString("\\f")
        default:
            newS.WriteRune(c)
        }
    }
    return newS.String()
}

type PolyEvalType struct {
    typeStr string
    typeName string
    valueType *PolyEvalType
    keyType *PolyEvalType
}

func newPolyEvalType(typeStr string) *PolyEvalType {
    this := new(PolyEvalType)
    this.typeStr = typeStr
    if !strings.Contains(typeStr, "<") {
        this.typeName = typeStr
    } else {
        idx := strings.Index(typeStr, "<")
        this.typeName = typeStr[0:idx]
        otherStr := typeStr[idx + 1:len(typeStr) - 1]
        if !strings.Contains(otherStr, ",") {
            this.valueType = newPolyEvalType(otherStr)
        } else {
            idx := strings.Index(otherStr, ",")
            this.keyType = newPolyEvalType(otherStr[0:idx])
            this.valueType = newPolyEvalType(otherStr[idx + 1:])
        }
    }
    return this
}

func genVoid(value interface{}) string {
    if value != nil {
        panic("value not nil")
    }
    return "nil"
}

func genInt(value interface{}) string {
    v, ok := value.(int)
    if !ok {
        panic("value not int")
    }
    return strconv.Itoa(v)
}

func genLong(value interface{}) string {
    v, ok := value.(int64)
    if !ok {
        panic("value not int64")
    }
    return strconv.FormatInt(v, 10) + "L"
}

func genDouble(value interface{}) string {
    f, ok := value.(float64)
    if !ok {
        panic("value not float64")
    }
    if math.IsNaN(f) {
        return "nan"
    } else if math.IsInf(f, 1) {
        return "inf"
    } else if math.IsInf(f, -1) {
        return "-inf"
    }
    valueStr := fmt.Sprintf("%.6f", f)
    for strings.HasSuffix(valueStr, "0") {
        valueStr = valueStr[0:len(valueStr) - 1]
    }
    if strings.HasSuffix(valueStr, ".") {
        valueStr += "0"
    }
    if valueStr == "-0.0" {
        valueStr = "0.0"
    }
    return valueStr
}

func genBool(value interface{}) string {
    v, ok := value.(bool)
    if !ok {
        panic("value not bool")
    }
    if v {
        return "true"
    } else {
        return "false"
    }
}

func genChar(value interface{}) string {
    v, ok := value.(rune)
    if !ok {
        panic("value not rune")
    }
    return "'" + escapeString(string(v)) + "'"
}

func genString(value interface{}) string {
    v, ok := value.(string)
    if !ok {
        panic("value not string")
    }
    return "\"" + escapeString(v) + "\""
}

func genAny(value interface{}) string {
    switch value.(type) {
    case bool:
        return genBool(value)
    case int:
        return genInt(value)
    case int64:
        return genLong(value)
    case float64:
        return genDouble(value)
    case rune:
        return genChar(value)
    case string:
        return genString(value)
    }
    panic("value not valid")
}

func genList(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Slice {
        panic("value not slice")
    }
    sliceValue := reflect.ValueOf(value)
    anySlice := make([]interface{}, sliceValue.Len())
    for i := 0; i < sliceValue.Len(); i++ {
        anySlice[i] = sliceValue.Index(i).Interface()
    }
    vStrs := make([]string, 0)
    for _, val := range anySlice {
        vStrs = append(vStrs, toPolyEvalStrWithType(val, t.valueType))
    }
    vStr := strings.Join(vStrs, ", ")
    return "[" + vStr + "]"
}

func genMlist(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Slice {
        panic("value not slice")
    }
    sliceValue := reflect.ValueOf(value)
    anySlice := make([]interface{}, sliceValue.Len())
    for i := 0; i < sliceValue.Len(); i++ {
        anySlice[i] = sliceValue.Index(i).Interface()
    }
    vStrs := make([]string, 0)
    for _, val := range anySlice {
        vStrs = append(vStrs, toPolyEvalStrWithType(val, t.valueType))
    }
    vStr := strings.Join(vStrs, ", ")
    return "[" + vStr + "]"
}

func genUnorderedlist(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Slice {
        panic("value not slice")
    }
    sliceValue := reflect.ValueOf(value)
    anySlice := make([]interface{}, sliceValue.Len())
    for i := 0; i < sliceValue.Len(); i++ {
        anySlice[i] = sliceValue.Index(i).Interface()
    }
    vStrs := make([]string, 0)
    for _, val := range anySlice {
        vStrs = append(vStrs, toPolyEvalStrWithType(val, t.valueType))
    }
    sort.Strings(vStrs)
    vStr := strings.Join(vStrs, ", ")
    return "[" + vStr + "]"
}

func genDict(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Map {
        panic("value not map")
    }
    mapValue := reflect.ValueOf(value)
    anyMap := make(map[interface{}]interface{})
    for _, key := range mapValue.MapKeys() {
        anyMap[key.Interface()] = mapValue.MapIndex(key).Interface()
    }
    vStrs := make([]string, 0)
    for k, v := range anyMap {
        kStr := toPolyEvalStrWithType(k, t.keyType)
        vStr := toPolyEvalStrWithType(v, t.valueType)
        vStrs = append(vStrs, kStr + "=>" + vStr)
    }
    sort.Strings(vStrs)
    vStr := strings.Join(vStrs, ", ")
    return "{" + vStr + "}"
}

func genMdict(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Map {
        panic("value not map")
    }
    mapValue := reflect.ValueOf(value)
    anyMap := make(map[interface{}]interface{})
    for _, key := range mapValue.MapKeys() {
        anyMap[key.Interface()] = mapValue.MapIndex(key).Interface()
    }
    vStrs := make([]string, 0)
    for k, v := range anyMap {
        kStr := toPolyEvalStrWithType(k, t.keyType)
        vStr := toPolyEvalStrWithType(v, t.valueType)
        vStrs = append(vStrs, kStr + "=>" + vStr)
    }
    sort.Strings(vStrs)
    vStr := strings.Join(vStrs, ", ")
    return "{" + vStr + "}"
}

func genOptional(value interface{}, t *PolyEvalType) string {
    if reflect.TypeOf(value).Kind() != reflect.Ptr {
        panic("value not pointer: is " + reflect.TypeOf(value).Kind().String())
    }
    pointerValue := reflect.ValueOf(value)
    if pointerValue.IsNil() {
        return "nil"
    }
    ptr := pointerValue.Elem().Interface()
    return toPolyEvalStr(ptr, t.valueType)
}

func toPolyEvalStr(value interface{}, t *PolyEvalType) string {
    typeName := t.typeName
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
    panic("type not valid")
}

func toPolyEvalStrWithType(value interface{}, t *PolyEvalType) string {
    return toPolyEvalStr(value, t) + ":" + t.typeStr
}

func MyStringify(value interface{}, typeStr string) string {
    return toPolyEvalStrWithType(value, newPolyEvalType(typeStr))
}

$$code$$