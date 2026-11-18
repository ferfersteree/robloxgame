// Build V19: merge the animal collection + Animation150 into the V18 place and update script sources.
// usage: merge <v18.rbxl> <collection.rbxl> <out.rbxl> <edits.txt>
// edits.txt lines: "<instance path>|<source file>"  (existing script: replace Source)
//                  "+<parent path>|<Name>|<source file>"  (new ModuleScript)
use rbx_dom_weak::types::{Ref, Variant};
use rbx_dom_weak::{InstanceBuilder, WeakDom};
use std::fs::{self, File};
use std::io::{BufReader, BufWriter};

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

fn find_all(dom: &WeakDom, path: &str) -> Vec<Ref> {
    dom.descendants().filter(|i| path_of(dom, i.referent()) == path).map(|i| i.referent()).collect()
}

fn find_one(dom: &WeakDom, path: &str) -> Ref {
    let v = find_all(dom, path);
    assert!(v.len() == 1, "expected exactly one '{}', found {}", path, v.len());
    v[0]
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let mut dom = rbx_binary::from_reader(BufReader::new(File::open(&a[1]).unwrap())).unwrap();
    let mut col = rbx_binary::from_reader(BufReader::new(File::open(&a[2]).unwrap())).unwrap();

    // 1. move collection data and the Animation150 library into ReplicatedStorage
    let rs = find_one(&dom, "ReplicatedStorage");
    for name in ["Animation150", "SpearHunt_RenderData", "SpearHunt_BiomeNames"] {
        assert!(find_all(&dom, &format!("ReplicatedStorage/{}", name)).is_empty(), "{} already exists", name);
        let r = find_one(&col, &format!("ReplicatedStorage/{}", name));
        col.transfer(r, &mut dom, rs);
        println!("moved ReplicatedStorage/{}", name);
    }

    // 2. script edits and new modules
    for line in fs::read_to_string(&a[4]).unwrap().lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if let Some(rest) = line.strip_prefix('+') {
            let p: Vec<&str> = rest.split('|').collect();
            let parent = find_one(&dom, p[0]);
            let src = fs::read_to_string(p[2]).unwrap();
            let b = InstanceBuilder::new("ModuleScript").with_name(p[1]).with_property("Source", Variant::String(src));
            dom.insert(parent, b);
            println!("added {}/{}", p[0], p[1]);
        } else {
            let p: Vec<&str> = line.split('|').collect();
            let r = find_one(&dom, p[0]);
            let src = fs::read_to_string(p[1]).unwrap();
            let inst = dom.get_by_ref_mut(r).unwrap();
            assert!(matches!(inst.properties.get(&"Source".into()), Some(Variant::String(_))), "{} has no Source", p[0]);
            inst.properties.insert("Source".into(), Variant::String(src));
            println!("updated {}", p[0]);
        }
    }

    let kids: Vec<Ref> = dom.root().children().to_vec();
    let mut w = BufWriter::new(File::create(&a[3]).unwrap());
    rbx_binary::to_writer(&mut w, &dom, &kids).unwrap();
    println!("written {}", a[3]);
}
