extern crate sodiumoxide;

use sodiumoxide::crypto::secretstream::{gen_key, Stream, Tag};
use std::io;
use std::io::prelude::*;

fn main() -> io::Result<()> {

    sodiumoxide::init();

    const BUFF_SIZE: usize = 500000;

    let stdin = io::stdin(); //implicit lock due to only using it one
    let mut buffer = stdin.take(BUFF_SIZE as u64); //this could be unsafe on a 128 bit computer, get off my back Rust

    let mut block = Vec::new();

    let key = gen_key();
    let (mut enc_stream, header) = Stream::init_push(&key)
                                        .unwrap();
    let mut i = buffer.read_to_end(&mut block)?;
    
    let c_text = enc_stream.push(&block, None, Tag::Message)
                    .unwrap();
    buffer.set_limit(BUFF_SIZE as u64); //unsafe yada 128 bit yada yada

    while i == BUFF_SIZE {
        i = buffer.read_to_end(&mut block)?;
        let c_text = enc_stream.push(&block, None, Tag::Message)
                        .unwrap();
        
        buffer.set_limit(BUFF_SIZE as u64); //unsafe yada 128 bit yada yada
    }
    

    Ok(())
}
