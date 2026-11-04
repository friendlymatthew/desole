use desolate::deflate;

use std::fs;
use std::hint::black_box;

const CORPUS: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/tests/data/infcover/window_end.deflate"
);

fn main() {
    let input = fs::read(CORPUS).unwrap();
    for _ in 0..100_000 {
        black_box(deflate::decode(black_box(&input)).unwrap());
    }
}
