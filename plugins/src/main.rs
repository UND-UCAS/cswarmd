extern crate sodiumoxide;

use sodiumoxide::crypto::secretstream::{gen_key, Stream, Tag};
use std::io;
use std::io::prelude::*;

const BUFF_SIZE: usize = 1000; //this controls the size of the blocks computed at a time, performance changes can be quite dramatic based on changes here.
    //a way to improve performance on the overall system would likely be to enforce some overall
    //constraints on message formatting, such as making sure messages are null terminated so that
    //we could switch to a buffered reader and read to the end of a message, encrypt it and send it
    //out. working with data as an arbitrary, unending stream does have dissadvantages that are
    //incurred in exchange for the flexibility it brings. Extensive testing could likely yeild a
    //fairly effecient block size and resolve most of these issues however.



fn main() -> io::Result<()> {

    argparse();

    sodiumoxide::init();

    let stdin = io::stdin(); //implicit lock due to only using it onece
    let mut buffer = stdin.take(BUFF_SIZE as u64); //this could be unsafe on a 128 bit computer, get off my back Rust

    let mut stdout = io::stdout();

    let mut block = Vec::new();

    let key = gen_key();
    let (mut enc_stream, header) = Stream::init_push(&key)
                                        .unwrap();
    let mut i = BUFF_SIZE; 
    while i == BUFF_SIZE {
        i = buffer.read_to_end(&mut block)?;
        let c_text = enc_stream.push(&block, None, Tag::Message)
                        .unwrap();

        stdout.write_all(&c_text);
        
        buffer.set_limit(BUFF_SIZE as u64); //unsafe yada 128 bit yada yada
    }
    

    Ok(())
}

fn argparse() {
    let args: Vec<String> = env::args().collect();
}

fn dec() -> io::Result<()> {

    let stdin = io::stdin(); //implicit lock due to only using it onece
    let mut buffer = stdin.take(BUFF_SIZE as u64); //this could be unsafe on a 128 bit computer, get off my back Rust

    let mut stdout = io::stdout();

    let mut block = Vec::new();

    let key = None;
    let (mut dec_stream, header) = Stream::init_pull(&header, &key)
                                        .unwrap();
    let mut i = BUFF_SIZE; 
    while i == BUFF_SIZE {
        i = buffer.read_to_end(&mut block)?;
        let (d_text, tag) = dec_stream.pull(&block, None)
                        .unwrap();
        if tag != Tag::Message {
            return Err(());
        }

        stdout.write_all(&d_text);
        
        buffer.set_limit(BUFF_SIZE as u64); //unsafe yada 128 bit yada yada
    }
    

    Ok(())
}

fn enc() -> io::Result<()> {

    let stdin = io::stdin(); //implicit lock due to only using it one
    let mut buffer = stdin.take(BUFF_SIZE as u64); //this could be unsafe on a 128 bit computer, get off my back Rust

    let mut stdout = io::stdout();

    let mut block = Vec::new();

    let key = gen_key();
    let (mut enc_stream, header) = Stream::init_push(&key)
                                        .unwrap();
    let mut i = BUFF_SIZE; 
    while i == BUFF_SIZE {
        i = buffer.read_to_end(&mut block)?;
        let c_text = enc_stream.push(&block, None, Tag::Message)
                        .unwrap();

        stdout.write_all(&c_text);
        
        buffer.set_limit(BUFF_SIZE as u64); //unsafe yada 128 bit yada yada
    }

    Ok(())
}
