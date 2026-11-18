// Dump Workspace parts (path, size, cframe, collision flags) and SurfaceGuis with their text as JSON lines.
use rbx_dom_weak::types::{Ref, Variant};
use rbx_dom_weak::WeakDom;
use std::fs::File;
use std::io::BufReader;

fn path_of(dom: &WeakDom, r: Ref) -> String {
    let mut names = Vec::new();
    let mut cur = r;
    while let Some(i) = dom.get_by_ref(cur) {
        if cur == dom.root_ref() {
            break;
        }
        names.push(i.name.clone());
        cur = i.parent();
    }
    names.reverse();
    names.join("/")
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let dom = rbx_binary::from_reader(BufReader::new(File::open(&a[1]).unwrap())).unwrap();
    let prefix = a.get(2).cloned().unwrap_or("Workspace/Map".to_string());
    for inst in dom.descendants() {
        let path = path_of(&dom, inst.referent());
        if !path.starts_with(&prefix) {
            continue;
        }
        let p = |k: &str| inst.properties.get(&k.into());
        match inst.class.as_str() {
            "Part" | "WedgePart" | "MeshPart" | "UnionOperation" | "CornerWedgePart" | "TrussPart" | "SpawnLocation" => {
                let size = match p("Size") { Some(Variant::Vector3(v)) => [v.x, v.y, v.z], _ => [0.0; 3] };
                let (pos, rot) = match p("CFrame") {
                    Some(Variant::CFrame(c)) => ([c.position.x, c.position.y, c.position.z],
                        [c.orientation.x.x, c.orientation.x.y, c.orientation.x.z, c.orientation.y.x, c.orientation.y.y, c.orientation.y.z, c.orientation.z.x, c.orientation.z.y, c.orientation.z.z]),
                    _ => ([0.0; 3], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]),
                };
                let tr = match p("Transparency") { Some(Variant::Float32(t)) => *t, _ => 0.0 };
                let cc = match p("CanCollide") { Some(Variant::Bool(b)) => *b, _ => true };
                let cq = match p("CanQuery") { Some(Variant::Bool(b)) => *b, _ => true };
                let ct = match p("CanTouch") { Some(Variant::Bool(b)) => *b, _ => true };
                let anch = match p("Anchored") { Some(Variant::Bool(b)) => *b, _ => false };
                let mat = match p("Material") { Some(Variant::Enum(e)) => e.to_u32(), _ => 256 };
                let col = match p("Color") { Some(Variant::Color3(c)) => [c.r, c.g, c.b], Some(Variant::Color3uint8(c)) => [c.r as f32 / 255.0, c.g as f32 / 255.0, c.b as f32 / 255.0], _ => [0.5; 3] };
                println!("{}", serde_json::json!({"k":"part","path":path,"c":inst.class,"size":size,"pos":pos,"rot":rot,"tr":tr,"cc":cc,"cq":cq,"ct":ct,"an":anch,"mat":mat,"col":col}));
            }
            "SurfaceGui" => {
                let face = match p("Face") { Some(Variant::Enum(e)) => e.to_u32(), _ => 5 };
                let mut texts = Vec::new();
                for d in dom.descendants_of(inst.referent()) {
                    if d.class == "TextLabel" || d.class == "TextButton" {
                        if let Some(Variant::String(s)) = d.properties.get(&"Text".into()) { texts.push(s.clone()); }
                    }
                }
                println!("{}", serde_json::json!({"k":"gui","path":path,"face":face,"texts":texts}));
            }
            "Sound" => {
                let id = match p("SoundId") { Some(Variant::ContentId(c)) => format!("{:?}", c), Some(Variant::String(s)) => s.clone(), _ => String::new() };
                println!("{}", serde_json::json!({"k":"sound","path":path,"id":id}));
            }
            _ => {}
        }
    }
}
