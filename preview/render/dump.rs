// Dump visible Parts of named models (Geometry folders) from an .rbxl as JSON for a 3D preview.
use rbx_dom_weak::types::{Variant, Ref};
use rbx_dom_weak::WeakDom;
use std::fs::File;
use std::io::BufReader;

fn find(dom: &WeakDom, root: Ref, path: &[&str]) -> Option<Ref> {
    let mut cur = root;
    for name in path {
        cur = *dom.get_by_ref(cur)?.children().iter().find(|c| dom.get_by_ref(**c).map(|i| i.name == *name).unwrap_or(false))?;
    }
    Some(cur)
}
fn collect(dom: &WeakDom, r: Ref, out: &mut Vec<serde_json::Value>) {
    let i = dom.get_by_ref(r).unwrap();
    if i.class == "Part" || i.class == "WedgePart" || i.class == "MeshPart" {
        let p = |k: &str| i.properties.get(&k.into());
        let size = match p("Size") { Some(Variant::Vector3(v)) => [v.x, v.y, v.z], _ => [1.0, 1.0, 1.0] };
        let (pos, rot) = match p("CFrame") {
            Some(Variant::CFrame(c)) => ([c.position.x, c.position.y, c.position.z],
                [c.orientation.x.x, c.orientation.x.y, c.orientation.x.z, c.orientation.y.x, c.orientation.y.y, c.orientation.y.z, c.orientation.z.x, c.orientation.z.y, c.orientation.z.z]),
            _ => ([0.0; 3], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]),
        };
        let col = match p("Color") { Some(Variant::Color3(c)) => [c.r, c.g, c.b], Some(Variant::Color3uint8(c)) => [c.r as f32 / 255.0, c.g as f32 / 255.0, c.b as f32 / 255.0], _ => [0.6, 0.6, 0.6] };
        let tr = match p("Transparency") { Some(Variant::Float32(t)) => *t, _ => 0.0 };
        let mat = match p("Material") { Some(Variant::Enum(e)) => e.to_u32(), _ => 256 };
        let shape = match p("Shape") { Some(Variant::Enum(e)) => e.to_u32(), _ => 1 };
        out.push(serde_json::json!({"n": i.name, "c": i.class, "size": size, "pos": pos, "rot": rot, "col": col, "tr": tr, "mat": mat, "shape": shape}));
    }
    for c in i.children() { collect(dom, *c, out); }
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dom = rbx_binary::from_reader(BufReader::new(File::open(&args[1]).unwrap())).unwrap();
    let mut res = serde_json::Map::new();
    for spec in &args[2..] {
        let path: Vec<&str> = spec.split('/').collect();
        let r = find(&dom, dom.root_ref(), &path).expect(spec);
        let mut v = Vec::new();
        collect(&dom, r, &mut v);
        res.insert(spec.clone(), serde_json::Value::Array(v));
    }
    println!("{}", serde_json::Value::Object(res));
}
