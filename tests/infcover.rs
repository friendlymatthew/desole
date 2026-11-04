use desolate::deflate;

use std::fs;
use std::path::Path;

fn check(path: &Path, input: Vec<u8>) -> datatest_stable::Result<()> {
    match fs::read(path.with_extension("out")) {
        Ok(expected) => {
            let out = deflate::decode(&input).map_err(|e| format!("valid stream rejected: {e}"))?;
            if out != expected {
                return Err(format!(
                    "wrong output ({} bytes, expected {})",
                    out.len(),
                    expected.len()
                )
                .into());
            }
        }
        Err(_) => {
            if deflate::decode(&input).is_ok() {
                return Err("invalid stream accepted".into());
            }
        }
    }
    Ok(())
}

datatest_stable::harness! {
    { test = check, root = "tests/data/infcover", pattern = r"\.deflate$" },
}
