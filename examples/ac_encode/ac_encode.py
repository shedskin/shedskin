## Arithmetic coding compressor and uncompressor for binary source.
## This is a cleaned-up version of AEncode.py

## (c) David MacKay - Free software. License: GPL

import os

BETA0=1;BETA1=1 ## default prior distribution
M = 30 ; ONE = (1<<M) ; HALF = (1<<(M-1))
QUARTER = (1<<(M-2)) ; THREEQU = HALF+QUARTER
def clear (c,charstack):
    ## print out character c, and other queued characters
    a = str(c) + str(1-c)*charstack[0]
    charstack[0]=0
    return a
    pass

def encode (string, c0=BETA0, c1=BETA1, adaptive=1,verbose=0):
    b=ONE; a=0;  tot0=0;tot1=0;     assert c0>0; assert c1>0
    if adaptive==0:
        p0 = c0*1.0/(c0+c1)
        pass
    ans=""
    charstack=[0] ## how many undecided characters remain to print
    for c in string:
        w=b-a
        if adaptive :
            cT = c0+c1
            p0 = c0*1.0/cT
            pass
        boundary = a + int(p0*w)
        if (boundary == a): boundary += 1; print("warningA"); pass # these warnings mean that some of the probabilities
        if (boundary == b): boundary -= 1; print("warningB"); pass # requested by the probabilistic model
        ## are so small (compared to our integers) that we had to round them up to bigger values
        if (c=='1') :
            a = boundary
            tot1 += 1
            if adaptive: c1 += 1.0 ; pass
        elif (c=='0'):
            b = boundary
            tot0 +=1
            if adaptive: c0 += 1.0 ; pass
            pass ## ignore other characters

        while ( (a>=HALF) or (b<=HALF) ) :   ## output bits
            if (a>=HALF) :
                ans = ans + clear(1,charstack)
                a = a-HALF
                b = b-HALF
            else :
                ans = ans + clear(0,charstack)
                pass
            a *= 2 ;      b *= 2
            pass

        assert a<=HALF; assert b>=HALF; assert a>=0; assert b<=ONE
        ## if the gap a-b is getting small, rescale it
        while ( (a>QUARTER) and (b<THREEQU) ):
            charstack[0] += 1
            a = 2*a-HALF
            b = 2*b-HALF
            pass

        assert a<=HALF; assert b>=HALF; assert a>=0; assert b<=ONE
        pass

    # terminate
    if ( (HALF-a) > (b-HALF) ) :
        w = (HALF-a)
        ans = ans + clear(0,charstack)
        while ( w < HALF ) :
            ans = ans + clear(1,charstack)
            w *=2
            pass
        pass
    else :
        w = (b-HALF)
        ans = ans + clear(1,charstack)
        while ( w < HALF ) :
            ans = ans + clear(0,charstack)
            w *=2
            pass
        pass
    return ans
    pass



def decode (string, N=10000, c0=BETA0, c1=BETA1, adaptive=1,verbose=0):
    ## must supply N, the number of source characters remaining.
    b=ONE ; a=0 ;      tot0=0;tot1=0  ;     assert c0>0 ; assert c1>0
    model_needs_updating = 1
    if adaptive==0:
        p0 = c0*1.0/(c0+c1)
        pass
    ans=""
    u=0 ; v=ONE
    for c in string :
        if N<=0 :
            break ## break out of the string-reading loop
        assert N>0
##    // (u,v) is the current "encoded alphabet" binary interval, and halfway is its midpoint.
##    // (a,b) is the current "source alphabet" interval, and boundary is the "midpoint"
        assert u>=0 ; assert v<=ONE
        halfway = u + (v-u)/2
        if( c == '1' ) :
            u = halfway
        elif ( c=='0' ):
            v = halfway
        else:
            pass
##    // Read bits until we can decide what the source symbol was.
##    // Then emulate the encoder's computations, and tie (u,v) to tag along for the ride.
        while (1): ## condition at end
            firsttime = 0
            if(model_needs_updating):
                w = b-a
                if adaptive :
                    cT = c0 + c1 ;   p0 = c0 *1.0/cT
                    pass
                boundary = a + int(p0*w)
                if (boundary == a): boundary += 1; print("warningA"); pass
                if (boundary == b): boundary -= 1; print("warningB"); pass
                model_needs_updating = 0
                pass
            if  ( boundary <= u ) :
                ans = ans + "1";             tot1 +=1
                if adaptive: c1 += 1.0 ; pass
                a = boundary ;	model_needs_updating = 1 ; 	N-=1
            elif ( boundary >= v )  :
                ans = ans + "0";             tot0 +=1
                if adaptive: c0 += 1.0 ; pass
                b = boundary ;	model_needs_updating = 1 ; 	N-=1
##	// every time we discover a source bit, implement exactly the
##	// computations that were done by the encoder (below).
            else :
##	// not enough bits have yet been read to know the decision.
                pass

##      // emulate outputting of bits by the encoder, and tie (u,v) to tag along for the ride.
            while ( (a>=HALF) or (b<=HALF) ) :
                if (a>=HALF) :
                    a = a-HALF ;  b = b-HALF ;    u = u-HALF ;     v = v-HALF
                    pass
                else :
                    pass
                a *= 2 ;      b *= 2 ;      u *= 2 ;      v *= 2
                model_needs_updating = 1
                pass

            assert a<=HALF;            assert b>=HALF;            assert a>=0;            assert b<=ONE
        ## if the gap a-b is getting small, rescale it
            while ( (a>QUARTER) and (b<THREEQU) ):
                a = 2*a-HALF;  b = 2*b-HALF ; u = 2*u-HALF ;  v = 2*v-HALF
                pass
            if not (N>0 and model_needs_updating) : ## this is the "while" for this "do" loop
                break
            pass
        pass
    return ans
    pass

def hardertest():
    print("Reading the BentCoinFile")
    inputfile = open( "testdata/BentCoinFile" , "r" )
    outputfile = open( "tmp.zip" , "w" )
    print("Compressing to tmp.zip")

    s = inputfile.read()
    N = len(s)
    zip = encode(s, 10, 1)
    outputfile.write(zip)
    outputfile.close();     inputfile.close()
    print("DONE compressing")

    inputfile = open( "tmp.zip" , "r" )
    outputfile = open( "tmp2" , "w" )
    print( "Uncompressing to tmp2")
    unc = decode(list(inputfile.read()), N, 10, 1)
    outputfile.write(unc)
    outputfile.close();     inputfile.close()
    print("DONE uncompressing")

    print("Checking for differences...")
    os.system( "diff testdata/BentCoinFile tmp2" )
    os.system( "wc tmp.zip testdata/BentCoinFile tmp2" )

def test():
    sl=["1010", "111", "00001000000000000000",\
        "1", "10" , "01" , "0" ,"0000000", \
        "000000000000000100000000000000000000000000000000100000000000000000011000000" ]
    for s in sl:
        print(("encoding", s))
        N=len(s)
        e = encode(s,10,1)
        print(("decoding", e))
        ds = decode(e,N,10,1)
        print(ds)
        if  (ds != s) :
            print(s)
            print("ERR@")
            pass
        else:
            print("ok ---------- ")
        pass
    pass

if __name__ == '__main__':
    test()
    hardertest()
