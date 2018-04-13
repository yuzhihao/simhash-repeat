Simhash Near-Duplicate Detection
================================
This library enables the identification of all fingerprints that are nearly
identical to a query fingerprint. In this context, a fingerprint is an unsigned
64-bit integer.

It also comes with an auxillary function designed to generate a fingerprint 
given a `char*` and a length. This fingeprint is generated with a tokenizer and
a hash function (both of which may be provided as template paramters). Using a 
cyclic hash function, it then performs simhash on a moving window of tokens (as
defined by the tokenizer).

The default hash function is `jenkins` hash and the default tokenizer splits on
non-alpha characters.

Building
========
This library links against [`libJudy`](http://judy.sourceforge.net/), which 
must be installed before building this. With that in place:

    cd src && make && ./test

For those curious about a testing performance, you can run the benchmark. It 
performs a number of insertions into the query data structure, and then 
performs 4 queries for each of those inserted fingerprints. Provide a number as
the first argument on the command line to change the number of items inserted.
To be clear, __this is done on merely one of the tables needed to perform 
simhash queries__.

    ./bench 10000000

Usage
=====
I'll work on this documentation as time permits, but for the time being, refer
to the source and `bench.cpp`.

Architecture
============
In this context, there is a large corpus of known fingerprints, and we would 
like to determine all the fingerprints that differ by our query by _k_ or fewer
bits. To accomplish this, we divide up the 64 bits into at _m_ blocks, where 
_m_ is greater than _k_. If hashes A and B differ by at most _k_ bits, then at
least _m - k_ groups are the same.

Choosing all the unique combinations of _m - k_ blocks, we perform a 
permutation on each of the hashes for the documents so that those blocks are 
first in the hash. Perhaps a picture would illustrate it better:

    63------53|52------42|41-----32|31------21|20------10|09------0|
    |    A    |     B    |    C    |     D    |     E    |    F    |
    
    If m = 6, k = 3, we'll choose permutations:
    - A B C D E F
    - A B D C E F
    - A B E C D F
    ...
    - C D F A B E
    - C E F A B D
    - D E F A B C

This generates a number of tables that can be put into sorted order, and then 
a small range of candidates can be found in each of those tables for a query, 
and then each candidate in that range can be compared to our query.

The corpus is represented by the union of these tables, could conceivably be
hosted on a separate machine. And each of these tables is also amenable to 
sharding, where each shard would comprise a contiguous range of numbers. For 
example, you might divide a table into 256 shards, where each shard is 
associated with each of the possible first bytes.

The best partitioning remains to be seen, likely from experimentation, but the
basis of this is the `table`. The `table` tracks hashes inserted into it 
subject to a permutation associated with the table. This permutation is 
described as a vector of bitmasks of contiguous bit ranges, whose populations 
sum to 64.

Example
=======

Let's suppose that our corpus has a fingerprint:

    0100101110111011001000101111101110111100001010011101100110110101

and we have a query:

    0100101110111011011000101111101110011100001010011100100110110101

and they differ by only three bits which happen to fall in blocks B, D and E:

    63------53|52------42|41-----32|31------21|20------10|09------0|
    |    A    |     B    |    C    |     D    |     E    |    F    |
    |         |          |         |          |          |         |
    0000000000000000010000000000000000100000000000000001000000000000

Since any fingerprint matching the query differs by at most 3 bits, at most 3
blocks can differ, and at least 3 must match. Whatever table has the 3 blocks 
that do not differ as the leading blocks will match the query when doing a 
scan. In this case, the table that's permuted `A C F B D E` will match. It's 
important to note that it's possible for a query to match from more than one 
table. For example, if two of the non-matching bits are in the same block, or 
the query differs by fewer than 3 bits.