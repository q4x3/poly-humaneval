use std::any::Any;
use std::vec::Vec;
use std::collections::HashMap;

fn escape_string(s: String) -> String {
    let mut new_s = String::new();
    for c in s.chars() {
        match c {
            '\\' => new_s.push_str("\\\\"),
            '"' => new_s.push_str("\\\""),
            '\n' => new_s.push_str("\\n"),
            '\t' => new_s.push_str("\\t"),
            '\r' => new_s.push_str("\\r"),
            _ => new_s.push(c),
        }
    }
    new_s
}

struct PolyEvalType {
    type_str: String,
    type_name: String,
    value_type: Option<Box<PolyEvalType>>,
    key_type: Option<Box<PolyEvalType>>,
}

impl PolyEvalType {
    fn new(type_str: String) -> PolyEvalType {
        let mut this = PolyEvalType {
            type_str: type_str.clone(),
            type_name: String::new(),
            value_type: None,
            key_type: None,
        };
        if !type_str.contains("<") {
            this.type_name = type_str.clone();
        } else {
            let idx = type_str.find("<").unwrap();
            this.type_name = type_str[0..idx].to_string();
            let other_str = type_str[idx + 1..type_str.len() - 1].to_string();
            if !other_str.contains(",") {
                this.value_type = Some(Box::new(PolyEvalType::new(other_str)));
            } else {
                let idx = other_str.find(",").unwrap();
                this.key_type = Some(Box::new(PolyEvalType::new(other_str[0..idx].to_string())));
                this.value_type = Some(Box::new(PolyEvalType::new(other_str[idx + 1..].to_string())));
            }
        }
        this
    }
}

trait MyStringifyPrivate {
    fn my_stringify_with_type(&self, t: &PolyEvalType) -> String {
        self.my_stringify_without_type(t) + ":" + &t.type_str
    }
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String;
}

impl MyStringifyPrivate for () {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "void" {
            panic!("type not match");
        }
        "null".to_string()
    }
}

impl MyStringifyPrivate for bool {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "bool" && t.type_name != "any" {
            panic!("type not match");
        }
        if *self {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }
}

impl MyStringifyPrivate for i32 {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "int" && t.type_name != "any" {
            panic!("type not match");
        }
        self.to_string()
    }
}

impl MyStringifyPrivate for i64 {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "long" && t.type_name != "any" {
            panic!("type not match");
        }
        self.to_string() + "L"
    }
}

impl MyStringifyPrivate for f64 {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "double" && t.type_name != "any" {
            panic!("type not match");
        }
        if self.is_nan() {
            "nan".to_string()
        } else if self.is_infinite() {
            if *self > 0.0 {
                "inf".to_string()
            } else {
                "-inf".to_string()
            }
        } else {
            let mut value_str = format!("{:.6}", self);
            while value_str.ends_with("0") {
                value_str = value_str[0..value_str.len() - 1].to_string();
            }
            if value_str.ends_with(".") {
                value_str += "0";
            }
            if value_str == "-0.0" {
                value_str = "0.0".to_string();
            }
            value_str
        }
    }
}

impl MyStringifyPrivate for char {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "char" && t.type_name != "any" {
            panic!("type not match");
        }
        format!("'{}'", escape_string(self.to_string()))
    }
}

impl MyStringifyPrivate for String {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "string" && t.type_name != "any" {
            panic!("type not match");
        }
        format!("\"{}\"", escape_string(self.to_string()))
    }
}

impl<T: MyStringifyPrivate> MyStringifyPrivate for Vec<T> {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "list" && t.type_name != "mlist" && t.type_name != "unorderedlist" {
            panic!("type not match");
        }
        let mut v_strs = Vec::new();
        for val in self {
            v_strs.push(val.my_stringify_with_type(t.value_type.as_ref().unwrap()));
        }
        if t.type_name == "unorderedlist" {
            v_strs.sort();
        }
        format!("[{}]", v_strs.join(", "))
    }
}

impl<K: MyStringifyPrivate, V: MyStringifyPrivate> MyStringifyPrivate for HashMap<K, V> {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "dict" && t.type_name != "mdict" {
            panic!("type not match");
        }
        let mut v_strs = Vec::new();
        for (k, v) in self {
            v_strs.push(format!("{}=>{}", k.my_stringify_with_type(t.key_type.as_ref().unwrap()), v.my_stringify_with_type(t.value_type.as_ref().unwrap())));
        }
        v_strs.sort();
        format!("{{{}}}", v_strs.join(", "))
    }
}

impl<T: MyStringifyPrivate> MyStringifyPrivate for Option<T> {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
        if t.type_name != "optional" {
            panic!("type not match");
        }
        if let Some(val) = self {
            val.my_stringify_with_type(t.value_type.as_ref().unwrap())
        } else {
            "null".to_string()
        }
    }
}

impl MyStringifyPrivate for Box<dyn Any> {
    fn my_stringify_without_type(&self, t: &PolyEvalType) -> String {
      if t.type_name != "any" {
            panic!("type not match");
        }
        if let Some(val) = self.downcast_ref::<bool>() {
            val.my_stringify_with_type(t)
        } else if let Some(val) = self.downcast_ref::<i32>() {
            val.my_stringify_with_type(t)
        } else if let Some(val) = self.downcast_ref::<i64>() {
            val.my_stringify_with_type(t)
        } else if let Some(val) = self.downcast_ref::<f64>() {
            val.my_stringify_with_type(t)
        } else if let Some(val) = self.downcast_ref::<char>() {
            val.my_stringify_with_type(t)
        } else if let Some(val) = self.downcast_ref::<String>() {
            val.my_stringify_with_type(t)
        } else {
            panic!("type not match");
        }
    }
}

pub trait MyStringify {
    fn my_stringify(&self, type_str: &str) -> String;
}

impl<T: MyStringifyPrivate> MyStringify for T {
    fn my_stringify(&self, type_str: &str) -> String {
        let t = PolyEvalType::new(type_str.to_string());
        self.my_stringify_with_type(&t)
    }
}