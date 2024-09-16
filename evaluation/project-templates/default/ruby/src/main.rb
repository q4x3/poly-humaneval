require 'digest'

module Utils
    extend self
    def escape_string(s)
        new_s = []
        for i in 0..s.length-1
            c = s[i]
            case c
            when "\\"
                new_s.push("\\\\")
            when "\""
                new_s.push("\\\"")
            when "\n"
                new_s.push("\\n")
            when "\t"
                new_s.push("\\t")
            when "\r"
                new_s.push("\\r")
            else
                new_s.push(c)
            end
        end
        return new_s.join("")
    end

    class PolyEvalType
        attr_accessor :type_str, :type_name, :value_type, :key_type
        def initialize(type_str)
            @type_str = type_str
            @type_name = ""
            @value_type = nil
            @key_type = nil
            if !type_str.include?("<")
                @type_name = type_str
                return
            else
                idx = type_str.index("<")
                @type_name = type_str[0..idx-1]
                other_str = type_str[idx+1..type_str.length-2]
                if !other_str.include?(",")
                    @value_type = PolyEvalType.new(other_str)
                else
                    idx = other_str.index(",")
                    @key_type = PolyEvalType.new(other_str[0..idx-1])
                    @value_type = PolyEvalType.new(other_str[idx+1..other_str.length-1])
                end
            end
        end
    end
    private_constant :PolyEvalType

    def gen_void(value)
        if value != nil
            raise "value is not null"
        end
        return "nil"
    end

    def gen_int(value)
        if !(value.is_a? Integer)
            raise "value is not integer"
        end
        return value.to_s
    end

    def gen_long(value)
        if !(value.is_a? Integer)
            raise "value is not integer"
        end
        return value.to_s + "L"
    end

    def gen_double(value)
        if !(value.is_a? Float or value.is_a? Integer)
            raise "value is not float"
        end
        f = value.to_f
        if f.nan?
            return "nan"
        elsif f == Float::INFINITY
            return "inf"
        elsif f == -Float::INFINITY
            return "-inf"
        end
        value_str = "%.6f" % f
        while value_str.end_with?("0")
            value_str = value_str[0..value_str.length-2]
        end
        if value_str.end_with?(".")
            value_str += "0"
        end
        if value_str == "-0.0"
            value_str = "0.0"
        end
        return value_str
    end

    def gen_bool(value)
        if !(value.is_a? TrueClass or value.is_a? FalseClass)
            raise "value is not boolean"
        end
        return value ? "true" : "false"
    end

    def gen_char(value)
        if !(value.is_a? String)
            raise "value is not string"
        end
        return "'" + escape_string(value) + "'"
    end

    def gen_string(value)
        if !(value.is_a? String)
            raise "value is not string"
        end
        return "\"" + escape_string(value) + "\""
    end

    def gen_any(value)
        if value.is_a? TrueClass or value.is_a? FalseClass
            return gen_bool(value)
        elsif value.is_a? Integer or value.is_a? Float
            return gen_double(value)
        elsif value.is_a? String
            return gen_string(value)
        end
        raise "value is not any"
    end

    def gen_list(value, t)
        if !value.is_a? Array
            raise "value is not array"
        end
        v_strs = []
        for v in value
            v_strs.push(to_poly_eval_str_with_type(v, t.value_type))
        end
        v_str = v_strs.join(", ")
        return "[" + v_str + "]"
    end

    def gen_mlist(value, t)
        if !value.is_a? Array
            raise "value is not array"
        end
        v_strs = []
        for v in value
            v_strs.push(to_poly_eval_str_with_type(v, t.value_type))
        end
        v_str = v_strs.join(", ")
        return "[" + v_str + "]"
    end

    def gen_unorderedlist(value, t)
        if !value.is_a? Array
            raise "value is not array"
        end
        v_strs = []
        for v in value
            v_strs.push(to_poly_eval_str_with_type(v, t.value_type))
        end
        v_strs.sort!
        v_str = v_strs.join(", ")
        return "[" + v_str + "]"
    end

    def gen_dict(value, t)
        if !value.is_a? Hash
            raise "value is not hash"
        end
        v_strs = []
        for key in value.keys
            val = value[key]
            k_str = to_poly_eval_str_with_type(key, t.key_type)
            v_str = to_poly_eval_str_with_type(val, t.value_type)
            v_strs.push(k_str + "=>" + v_str)
        end
        v_strs.sort!
        v_str = v_strs.join(", ")
        return "{" + v_str + "}"
    end

    def gen_mdict(value, t)
        if !value.is_a? Hash
            raise "value is not hash"
        end
        v_strs = []
        for key in value.keys
            val = value[key]
            k_str = to_poly_eval_str_with_type(key, t.key_type)
            v_str = to_poly_eval_str_with_type(val, t.value_type)
            v_strs.push(k_str + "=>" + v_str)
        end
        v_strs.sort!
        v_str = v_strs.join(", ")
        return "{" + v_str + "}"
    end

    def gen_optional(value, t)
        if value == nil
            return "nil"
        else
            return to_poly_eval_str(value, t.value_type)
        end
    end

    def to_poly_eval_str(value, t)
        type_name = t.type_name
        if type_name == "void"
            return gen_void(value)
        elsif type_name == "int"
            return gen_int(value)
        elsif type_name == "long"
            return gen_long(value)
        elsif type_name == "double"
            return gen_double(value)
        elsif type_name == "bool"
            return gen_bool(value)
        elsif type_name == "char"
            return gen_char(value)
        elsif type_name == "string"
            return gen_string(value)
        elsif type_name == "any"
            return gen_any(value)
        elsif type_name == "list"
            return gen_list(value, t)
        elsif type_name == "mlist"
            return gen_mlist(value, t)
        elsif type_name == "unorderedlist"
            return gen_unorderedlist(value, t)
        elsif type_name == "dict"
            return gen_dict(value, t)
        elsif type_name == "mdict"
            return gen_mdict(value, t)
        elsif type_name == "optional"
            return gen_optional(value, t)
        end
        raise "unknown type"
    end

    def to_poly_eval_str_with_type(value, t)
        return to_poly_eval_str(value, t) + ":" + t.type_str
    end

    def my_stringify(value, type_str)
        return to_poly_eval_str_with_type(value, PolyEvalType.new(type_str))
    end
    
end

def my_stringify(value, type_str)
    return Utils.my_stringify(value, type_str)
end

$$code$$