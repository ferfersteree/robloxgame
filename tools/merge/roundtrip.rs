// Round-trip test: decode an .rbxl, re-encode it with rbx_binary, decode again, compare every instance and property.
use rbx_dom_weak::types::Ref;
use rbx_dom_weak::WeakDom;
use std::fs::File;
use std::io::{BufReader, BufWriter};

fn walk(dom: &WeakDom, r: Ref, out: &mut Vec<Ref>) {
    out.push(r);
    for c in dom.get_by_ref(r).unwrap().children() {
        walk(dom, *c, out);
    }
}

fn main() {
    let a = std::env::args().nth(1).unwrap();
    let b = std::env::args().nth(2).unwrap();
    let dom = rbx_binary::from_reader(BufReader::new(File::open(&a).unwrap())).unwrap();
    {
        let mut w = BufWriter::new(File::create(&b).unwrap());
        let kids: Vec<Ref> = dom.root().children().to_vec();
        rbx_binary::to_writer(&mut w, &dom, &kids).unwrap();
    }
    let dom2 = rbx_binary::from_reader(BufReader::new(File::open(&b).unwrap())).unwrap();
    let (mut la, mut lb) = (Vec::new(), Vec::new());
    walk(&dom, dom.root_ref(), &mut la);
    walk(&dom2, dom2.root_ref(), &mut lb);
    println!("instances {} vs {}", la.len(), lb.len());
    let mut diffs = 0usize;
    let mut shown = 0usize;
    for (x, y) in la.iter().zip(lb.iter()) {
        let ia = dom.get_by_ref(*x).unwrap();
        let ib = dom2.get_by_ref(*y).unwrap();
        let mut bad = ia.class != ib.class || ia.name != ib.name || ia.children().len() != ib.children().len();
        if !bad {
            for (k, v) in ia.properties.iter() {
                match ib.properties.get(k) {
                    Some(v2) if format!("{:?}", v) == format!("{:?}", v2) => {}
                    Some(rbx_dom_weak::types::Variant::CFrame(c2)) if matches!(v, rbx_dom_weak::types::Variant::CFrame(_)) => {
                        if let rbx_dom_weak::types::Variant::CFrame(c1) = v {
                            let f = |a: f32, b: f32| (a - b).abs() > 1e-4;
                            let (o1, o2) = (c1.orientation, c2.orientation);
                            if f(c1.position.x, c2.position.x) || f(c1.position.y, c2.position.y) || f(c1.position.z, c2.position.z)
                                || f(o1.x.x, o2.x.x) || f(o1.x.y, o2.x.y) || f(o1.x.z, o2.x.z) || f(o1.y.x, o2.y.x) || f(o1.y.y, o2.y.y) || f(o1.y.z, o2.y.z)
                                || f(o1.z.x, o2.z.x) || f(o1.z.y, o2.z.y) || f(o1.z.z, o2.z.z) {
                                bad = true;
                                if shown < 8 { println!("CFRAME REAL DIFF {} {}", ia.class, ia.name); shown += 1; }
                            }
                        }
                    }
                    _ => {
                        // Ref properties differ by referent value only; compare loosely
                        if !matches!(v, rbx_dom_weak::types::Variant::Ref(_)) {
                            bad = true;
                            if shown < 8 {
                                println!("PROP DIFF {} {}.{}", ia.class, ia.name, k);
                                shown += 1;
                            }
                        }
                    }
                }
            }
            if ia.properties.len() != ib.properties.len() {
                bad = true;
                if shown < 8 {
                    println!("PROP COUNT {} {} {} vs {}", ia.class, ia.name, ia.properties.len(), ib.properties.len());
                    shown += 1;
                }
            }
        }
        if bad {
            diffs += 1;
        }
    }
    println!("instances differing: {}", diffs);
}
