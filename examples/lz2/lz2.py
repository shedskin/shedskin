#!/usr/bin/env python
"""
Lempel-Ziv code (2) for compression

This version of Lempel-Ziv looks back in the sequence read so far
for a match to the incoming substring; then sends a pointer.

It is a self-delimiting code that sends a special pointer indicating
end of file.

http://www.aims.ac.za/~mackay/itila/

  LZ2.py is free software (c) David MacKay December 2005. License: GPL
"""
## For license statement see  http://www.gnu.org/copyleft/gpl.html

import sys, os

def dec_to_bin( n , digits ):
    """ n is the number to convert to binary;  digits is the number of bits you want
    Always prints full number of digits
    >>> print dec_to_bin( 17 , 9)
    000010001
    >>> print dec_to_bin( 17 , 5)
    10001

    Will behead the standard binary number if requested
    >>> print dec_to_bin( 17 , 4)
    0001
    """
    if(n<0) :
        sys.stderr.write( "warning, negative n not expected\n")
    i=digits-1
    ans=""
    while i>=0 :
        b = (((1<<i)&n)>0)
        i -= 1
        ans = ans + str(int(b))
    return ans

def bin_to_dec( clist , c , tot=0 ):
    """Implements ordinary binary to integer conversion if tot=0
    and HEADLESS binary to integer if tot=1
    clist is a list of bits; read c of them and turn into an integer.
    The bits that are read from the list are popped from it, i.e., deleted

    Regular binary to decimal 1001 is 9...
    >>> bin_to_dec(  ['1', '0', '0', '1']  ,  4  , 0 )
    9

    Headless binary to decimal [1] 1001 is 25...
    >>> bin_to_dec(  ['1', '0', '0', '1']  ,  4  , 1 )
    25
    """
    while (c>0) :
        assert ( len(clist) > 0 ) ## else we have been fed insufficient bits.
        tot = tot*2 + int(clist.pop(0))
        c-=1
        pass
    return tot

def ceillog( n ) : ## ceil( log_2 ( n ))   [Used by LZ.py]
    """
    >>> print ceillog(3), ceillog(4), ceillog(5)
    2 2 3
    """
    assert n>=1
    c = 0
    while 2**c<n :
        c += 1
    return c

def status(fr,to,oldpointer,digits,digits2,length,c,maxlength):
    """
    Print out the current pointer location, the current matching
    string, and the current locations of "from" and "to".
    Also report the range of conceivable values for the pointer and
    length quantities.
    """
    print("fr,to = %d,%d; oldpointer=%d; d=%d, d2=%d, l=%d" % \
          (fr,to,oldpointer, digits,digits2, length))
    print("|%s\n|%s%s\t(pointer at %d/0..%d)\n|%s%s\t(maximal match of length %d/0..%d)\n|%s%s\n|%s%s" %\
          (c,\
           '.'*oldpointer,'p', oldpointer, fr-1, \
           ' '*oldpointer, '-'*length, length, maxlength,\
           ' '*fr, 'f',\
           ' '*to, 't'))

def searchstatus(fr,to,L,c):
    """
    Show the current string (fr,to) that is being searched for.
    """
    print("L=%d, fr=%d, to=%d" % (L,fr, to))
    print("|%s\n|%s%s\n|%s%s" %\
          (c,\
           ' '*fr, 'f',\
           ' '*to, 't'))
    # find where this substring occurs
    print("looking for '%s' inside '%s'. " % (c[fr:to],c[0:fr]), end=' ')

def encode ( c, pretty=1 , verbose=0 ): ## c is STRING of characters (0/1) ; p is whether to print out prettily
    """
    Encode using Lempel-Ziv (2), which sends pointers and lengths
    Pretty printing
    >>> print encode("000000000000100000000000",1)
    0(0,1)(00,10)(000,100)(0000,0100)(1101,0)(0000,1011)

    Normal printing
    >>> print encode("000000000000100000000000",0)
    0010010000100000001001101000001011

    To understand the encoding procedure it might be
    best to read the decoder.

    Termination rule:
    We have a special reserved "impossible pointer" string
    and always have space for one extra one in the pointer area, to allow us to
    send termination information, including whether the last bit needed removing or not.
    If the last thing that happened was a perfect match without mismatch event,
    which is the most common event, do nothing, send EOF. The decoder will sees the special
    '0' bit after the special pointer and so does not include the final character.
    If instead there happened to be a mismatch event at the exact moment
    when the final char arrived, we do a standard decoding action.

    ::-----SEQUENCE SO FAR-------::|--SEQUENCE STILL to be sent--
         ^pointer                   ^fr         ^to
         ------------               ------------
         <- length ->               <- length ->
    Once we have found the maximum length (to-fr) that matches, send
         the values of pointer and length.

    """
    output =[]
    L = len(c)
    assert L>1 ## sorry, cannot compress the files "0" or "1" or ""
    output.append( c[0] )     # to get started we must send one bit
    fr = 1 ;
    eof_sent = 0
    while (eof_sent == 0 ) : # start a new substring search
        to = fr              # Always Start by finding a match of the empty string
        oldpointer = -2      # indicates that no match has been found. Used for debugging.
        while  (eof_sent == 0 ) and (to<=L) :   # extend the search
            if verbose > 2:  searchstatus(fr,to,L,c);  pass
            pointer = c[0:fr].find( c[fr:to] )
            if verbose > 2: print("result:",pointer , to) ; pass
            if ( pointer == -1) or (to>=L ) :
                if (pointer!=-1): oldpointer = pointer ;  pass
                digits  = ceillog ( fr+1 )  # digits=ceillog ( fr ) would be enough space for oldpointer, which is in range (0,fr-1).
                # we give ourselves extra space so as to be able to convey a termination event
                maxlength = fr-oldpointer  # from-oldpointer is maximum possible sequence length
                digits2 = ceillog ( maxlength+1 )
                if (pointer==-1) :    to -= 1 ; pass # the matched string was shorter than to-fr; need to step back.
                length = to-fr
                if length < maxlength: # then the receiver can deduce the next bit
                    to += 1 ;                     pass
                if (to>=L) : # Special termination message precedes the last (pointer,length) message.
                    if (pointer!=-1) : specialbit = 0 ; pass
                    else :             specialbit = 1 ; pass
                    output.append( printout(dec_to_bin( fr , digits ) ,
                                            str(specialbit)  ,             pretty ) )
                    eof_sent=1
                    pass
                assert length<=maxlength
                output.append( printout(dec_to_bin( oldpointer , digits ) ,
                                        dec_to_bin( length , digits2 ) ,   pretty ) )
                if verbose:
                    status(fr,to,oldpointer,digits,digits2,length,c,maxlength)
                    print("".join(output))
                    pass
                oldpointer = -2
                fr = to
                break
            else:
                to += 1 ;                 oldpointer = pointer ; pass
            pass
        pass
    if verbose: print("DONE Encoding")
    return "".join(output)

def printout( pointerstring, lengthstring,  pretty=1):
    if pretty:
        return "("+pointerstring+","+lengthstring+")"
    else:
        return pointerstring+lengthstring

def decode( li , verbose=0 ):
    """
    >>> print decode(list("0010010000100000001001101000001010"))
    00000000000010000000000
    """
    assert(len(li)>0) # need to get first bit! The compressor cannot compress the empty string.
    c=li.pop(0)
    fr = 1 ; to = fr

    not_eof = 1 ; specialbit=0
    while not_eof:
        assert(len(li)>0) # self-delimiting file
        digits  = ceillog ( fr+1 )
        pointer = bin_to_dec( li , digits ) # get the pointer
        maxlength = fr-pointer
        if pointer==fr : # special end of file signal!
            specialbit=int(li.pop(0))
            pointer = bin_to_dec( li , digits )
            maxlength = fr-pointer
            not_eof = 0
            pass
        digits2 = ceillog ( maxlength+1 ) 
        length  =  bin_to_dec( li , digits2 )
        addition = c[pointer:pointer+length] ; assert len(addition) == length
        if  ( (not_eof==0 ) and (specialbit==1)) or (not_eof and (length<maxlength)):
            opposite = str(1-int(c[pointer+length]))
        else :
            opposite = ''
        c = c + addition + opposite
        if verbose:
            to = length + fr + 1
            status(fr,to,pointer,digits,digits2,length,c,maxlength)
            pass
        fr = len(c)
    return c

def test():
    print("pretty encoding examples:")
    examples = [  "0010000000001000000000001" ,  "00000000000010000000000"  ]
    examples2= [ "1010101010101010101010101010101010101010",\
                     "011",\
                 "01","10","11", "00", "000","001","010","011","100","101","110",\
                 "1010100000000000000000000101010101010101000000000000101010101010101010",\
                 "10101010101010101010101010101010101010101",\
                 "00000","000000","0000000","00000000","000000000","0000000000",\
                 "00001","000001","0000001","00000001","000000001","0000000001",\
                 "0000","0001","0010","0011","0100","0101","0110",\
                 "0111","1000","1001","1010","1011","1100","1101","1110","1111",\
                 "111","110010010101000000000001110100100100000000000000", \
                 "00000000000010000000000" , "1100100" ,  "100100" ]
    pretty = 1 ; verbose = 1
    for ex in examples :
        print()
        print("Encoding", ex)
        zip =  encode( ex , pretty , verbose )
        if verbose>2: print(zip)
        zip2 =  encode( ex , 0 , 0 )
        print("Decoding", zip2)
        unc = decode( list(zip2) , verbose )
        print("-> ", unc)
        if unc==ex:
            print("OK!")
        else:
            print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!")
            assert False

    if(0):
        pretty = 1 ; verbose = 1
        for ex in examples2 :
            zip =  encode( ex , pretty , verbose )
            print(zip)
            zip2 =  encode( ex , 0 , 0 )
            print("Decoding", zip2)
            unc = decode( list(zip2) , verbose )
            print("-> ", unc)
            if unc==ex:
                print("OK!")
            else:
                print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!")
                assert False
        print("decoding examples:")
        examples = [ "0010010000100000001001101000001001"]
        for ex in examples :
            print(ex, decode( list(ex) , verbose ))

def hardertest():
    print("Reading the BentCoinFile")
    inputfile = open( "testdata/BentCoinFile" , "r" )
    outputfile = open( "tmp.zip" , "w" )
    print("Compressing to tmp.zip")

    zip = encode(inputfile.read(), 0, 0)
    outputfile.write(zip)
    outputfile.close();     inputfile.close()
    print("DONE compressing")

    inputfile = open( "tmp.zip" , "r" )
    outputfile = open( "tmp2" , "w" )
    print("Uncompressing to tmp2")
    unc = decode(list(inputfile.read()), 0)
    outputfile.write(unc)
    outputfile.close();     inputfile.close()
    print("DONE uncompressing")

    print("Checking for differences...")
    os.system( "diff testdata/BentCoinFile tmp2" )
    os.system( "wc tmp.zip testdata/BentCoinFile tmp2" )

if __name__ == '__main__':
    test()
    hardertest()
