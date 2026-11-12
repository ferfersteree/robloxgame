use mlua::{Lua, Table, Value, Result};
fn json_to_lua(lua: &Lua, v: &serde_json::Value) -> Result<Value> {
    Ok(match v {
        serde_json::Value::Null => Value::Nil,
        serde_json::Value::Bool(b) => Value::Boolean(*b),
        serde_json::Value::Number(n) => Value::Number(n.as_f64().unwrap()),
        serde_json::Value::String(s) => Value::String(lua.create_string(s)?),
        serde_json::Value::Array(a) => {
            let t = lua.create_table()?;
            for (i, x) in a.iter().enumerate() { t.set(i + 1, json_to_lua(lua, x)?)?; }
            Value::Table(t)
        }
        serde_json::Value::Object(o) => {
            let t = lua.create_table()?;
            for (k, x) in o { t.set(k.as_str(), json_to_lua(lua, x)?)?; }
            Value::Table(t)
        }
    })
}
fn main() -> Result<()> {
    let lua = Lua::new();
    let g = lua.globals();
    g.set("readfile", lua.create_function(|_, p: String| std::fs::read_to_string(&p).map_err(mlua::Error::external))?)?;
    g.set("jsondecode", lua.create_function(|lua, s: String| {
        let v: serde_json::Value = serde_json::from_str(&s).map_err(mlua::Error::external)?;
        json_to_lua(lua, &v)
    })?)?;
    g.set("loadmod", lua.create_function(|lua, (src, name, env): (String, String, Table)| {
        lua.load(&src).set_name(name).set_environment(env).into_function()
    })?)?;
    let script = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap();
    lua.load(&script).set_name("run").exec()
}
