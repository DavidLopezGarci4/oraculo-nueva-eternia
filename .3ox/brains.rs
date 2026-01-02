// ▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
// ▛//▞▞ ⟦⎊⟧ :: ⧗-25.131 ▸ ρ{agent.brain}.φ{identity}.τ{rules}.λ{bind} ⫸ :: BRAIN.RS
//
// Nueva Eternia High-Performance Kernel
// Version: v2.1.0 

use std::env;
use std::collections::HashSet;

pub fn jaccard_similarity(s1: &str, s2: &str) -> f64 {
    let set1: HashSet<char> = s1.to_lowercase().chars().filter(|c| c.is_alphanumeric()).collect();
    let set2: HashSet<char> = s2.to_lowercase().chars().filter(|c| c.is_alphanumeric()).collect();
    
    if set1.is_empty() && set2.is_empty() { return 1.0; }
    
    let intersection = set1.intersection(&set2).count();
    let union = set1.union(&set2).count();
    
    intersection as f64 / union as f64
}

pub fn match_logic(name1: &str, name2: &str, ean1: Option<&str>, ean2: Option<&str>) -> (bool, f64) {
    // Rule: EAN Priority
    if let (Some(e1), Some(e2)) = (ean1, ean2) {
        if e1 == e2 && !e1.is_empty() {
            return (true, 1.0);
        }
    }
    
    let score = jaccard_similarity(name1, name2);
    (score >= 0.7, score)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Oráculo de Nueva Eternia :: Rust Kernel Ready");
        return;
    }

    match args[1].as_str() {
        "match" => {
            if args.len() < 4 {
                println!("Error: match requires <name1> <name2> [ean1] [ean2]");
                return;
            }
            let name1 = &args[2];
            let name2 = &args[3];
            let ean1 = args.get(4).map(|s| s.as_str());
            let ean2 = args.get(5).map(|s| s.as_str());
            
            let (is_match, score) = match_logic(name1, name2, ean1, ean2);
            println!("MATCH_RESULT|{}|{:.4}", is_match, score);
        }
        _ => eprintln!("Command not recognized"),
    }
}
