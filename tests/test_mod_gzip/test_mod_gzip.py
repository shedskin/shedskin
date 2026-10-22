import base64
import gzip
import os

# generated with CPython's gzip and zlib modules


def make_data(n):
    words = [b'another', b'world', b'lester', b'buddy', b'arena', b'jail', b'water', b'city']
    out = bytearray()
    x = 12345
    while len(out) < n:
        x = (x * 1103515245 + 12345) & 0x7fffffff
        out += words[x % 8]
        out += b' ' if x & 0x100 else b'\n'
        if x % 97 == 0:
            out += bytes([x >> 16 & 0xff, x >> 8 & 0xff])
    return bytes(out[:n])


# make_data(60000), compresslevel 9: dynamic huffman blocks, distances up to 32K
BIG = base64.b64decode(
    'H4sIAAAAAAAC/+3bS0hUURzH8XxgciBoEbTR+lsEUlgthMKinUgGQxa1qc3UDKTISKM5TSRUi6CI'
    'JMIiIqKFLUqIqEUWWCBUEKSLDMoQI8NWLSKCFj1Qo8z7OOc6M3fuHb/bgcOc97kffuekoh3xpDrY'
    '3JGWaDKeiKqWaHOrao23T/184EgsllbRRFvHoXhSKodSbcnWmKSmisicImJbZG4B1fpUU0RNF1Gp'
    'v9VSmmopfaXEplKz/mGmgDg3XF8lca+SsvyDGLdBObdBbNsgugJzqyQeGi3z6lbtSIv9OIh7AWU0'
    'cFJXYz6bxH4kRDP9LM22TnCxGWtlMjnEvtnO/yD2Heu8IpT9bLJOPzFYEWb/4LSEJF5pXinl3k9O'
    '80kMOlZ52JtEM9au/aTc17XuH8Sll8TDVmOd4GK+c4hJo53HQek3ZHGvkmiqJPoqOS9ScZvgYtCt'
    '2kVqtG/8KfD66/ymn+sEF4PNTGmbvanbbZmadK12tJX5/mewJsTgJPIyxZVmAnr4IjDYwzXHinj4'
    '5jBaE+Jy/IqHL7P//uFTtcnRZfaZ4mF3EvMtWZl+aml2J7OPOaODS7lMjsy+nDI84JXX0zojSyAJ'
    'JOGXJKpu679gkUSgJFFIjihtRBJIIruSCKwjUITT5CtpwhHGGw2K0GyWPeM4AkeE3hGJeyHMJCxD'
    't7ciH5JorAqUJc5WoQlSCSyBJbDEv1560EMmgSVIJJAEkiCRMDiDyCMQRNYE0d+FITAEhvDJEE/q'
    'uNfkuF1evO+/Itb+8NkR7775J4kXMSyBJYJviVNlaAJNZK6J3RE8QSJRMJoYX4In8ASvJEgkSCRQ'
    'BIowTCQabqGIQlHE1iJSCRSRD0Us7ySVQBEoIiyKiCzGETjCL0e8uYQkQiCJ4dX5ud009szSjkff'
    '0UQ2NPHzOnecpgqMPcyCJwYnEMXsAscWFXIykdiDKTAFpiCZQBQkE3iCtxLkEryVCFIqcbo3FIoo'
    'H8gwmbhw19pXn3kxgSNwBI7AETgCR2TBETciQZHE2+e5t8TIFjRRMJooGccTZBK8lcAROAJH4Agc'
    'gSPII8gjEAR5hO9+mDzukyCufsEQeTdE2cmFo4hIn8PucaYaSSAJJIEkkASSQBJhlET/5HSlduxD'
    'E6QRSCLUacTLGvKITBWRrMUROAJH4AgDR4weRhJIAkmQSeRYEcmdOAJHcKuJW03zMURty8JVRPko'
    'jigERzwuJpHIhyOa1iMJJIEkCiuPeLUZSSAJJBEMSWw/wb2mQEuiboJEgkQiq464fJS7TTgCR+AI'
    '7jWhCBSBIngb4bgeVg3kQxHXGrjXhCJ4H4EhMASGcDNEvA9FoAgUkZYV9TgipI6408Qra15HoAgU'
    'sSAUUb3RsyO21SMJJEEagSNy7Ihla5AEjvDXEcMVJBJBdcS5DUgCSfgviZU3A2iJoU4yCSSBJJAE'
    'kiCRwBG+OaJ0hJtNOXFEuotEwq5Adx+SyJ0kittJJXAEjsAROAJH4Agc4cERE70hfyHxqyzYklh3'
    'Pv+ZxIel3G5CEtxuCosjivbPFBnchSWwBJbAElgCS3C3iUSCFxJZNsSV9ygCRZBGmAji429n52Te'
    'YOoAAA==')

# fixed huffman
SMALL = base64.b64decode('H4sIAAAAAAAC/8tIzcnJV8hAkACAiPnlEQAAAA==')

# compresslevel 0: stored blocks
STORED = base64.b64decode(
    'H4sIAAAAAAAE/wHoAxf8d2F0ZXIKY2l0eSBhcmVuYQpqYWlsCmxlc3RlcgpidWRkeQphbm90aGVy'
    'IB3Pd29ybGQgd2F0ZXIgY2l0eSBhcmVuYQpqYWlsIGxlc3RlcgpidWRkeQphbm90aGVyIHdvcmxk'
    'IHdhdGVyIGNpdHkKbMZhcmVuYQpqYWlsIGxlc3RlcgpidWRkeQphbm90aGVyCndvcmxkCndhdGVy'
    'CmNpdHkKYXJlbmEKamFpbApsZXN0ZXIKYnVkZHkKYW5vdGhlcgp3b3JsZCB3YXRlciBjaXR5IGFy'
    'ZW5hCmphaWwgbGVzdGVyIGJ1ZGR5CmFub3RoZXIgd29ybGQKd2F0ZXIKY2l0eSBhcmVuYSBqYWls'
    'Cmxlc3RlcgpidWRkeQphbm90aGVyIHdvcmxkCndhdGVyCmNpdHkKYXJlbmEKamFpbApsZXN0ZXIg'
    'YnVkZHkKYW5vdGhlcgp3b3JsZCB3YXRlciBjaXR5CmFyZW5hIGphaWwKbGVzdGVyIGJ1ZGR5CmFu'
    'b3RoZXIKd29ybGQgd2F0ZXIgY2l0eSBhcmVuYQpqYWlsCmxlc3RlciBidWRkeQphbm90aGVyIHdv'
    'cmxkIHdhdGVyCmNpdHkgYXJlbmEgamFpbCBsZXN0ZXIgYnVkZHkKYW5vdGhlciB3b3JsZCB3YXRl'
    'ciBjaXR5CmFyZW5hIGphaWwgbGVzdGVyCmJ1ZGR5CmFub3RoZXIgd29ybGQKd2F0ZXIKY2l0eQph'
    'cmVuYSBqYWlsIGxlc3RlciBidWRkeQphbm90aGVyIHdvcmxkCndhdGVyCmNpdHkgYXJlbmEgamFp'
    'bCBsZXN0ZXIKYnVkZHkKYW5vdGhlcgp3b3JsZAp3YXRlciBjaXR5IGFyZW5hIGphaWwKbGVzdGVy'
    'IGJ1ZGR5CmFub3RoZXIKd29ybGQKd2F0ZXIgY2l0eQphcmVuYSBqYWlsCmxlc3RlcgpidWRkeQph'
    'bm90aGVyIHdvcmxkIDotd2F0ZXIKY2l0eQphcmVuYQpqYWlsCmxlc3RlcgpidWRkeQphbm90aGVy'
    'IHdvcmxkIHdhdGVyIGNpdHkgYXJlbmEgamFpbApsZXN0ZXIKYnVkZHkKYW5vdGhlcgp3b3JsZAp3'
    'YXRlcgpjaXR5IGFyZW5hCmphaWwgbGVzdGVyCmJ1ZGR5IGFub3RoZXIKd29ybGQgd2F0ZXIKY2l0'
    'eQphcmVuYSBqYWlsCmxlc3RlciBidWRkeQphbm90aGVyIHdvcmxkCndhdGVyIGNpdHkKYXJlbmEK'
    'amFpbCBsZXN0ZXIKYnVkZHkgYW5vdGhlciB3b3JsZAp3YXRlciBjaXR5IGFyZfYqOzroAwAA')

EMPTY = base64.b64decode('H4sIAAAAAAAC/wMAAAAAAAAAAAA=')

# FEXTRA, FNAME, FCOMMENT and FHCRC
FIELDS = base64.b64decode('H4sIHgAAAAACAwMAeHl6bmFtZS50eHQAYSBjb21tZW50ABI0K88syVDISE1MSS1SSMtMzUkpBgD4WsZDEgAAAA==')


def error(data):
    try:
        gzip.decompress(data)
    except EOFError as e:
        return 'EOFError: ' + str(e)
    except gzip.BadGzipFile as e:
        return 'BadGzipFile: ' + str(e)
    return ''


def test_decompress():
    assert gzip.decompress(BIG) == make_data(60000)
    assert gzip.decompress(SMALL) == b'hello hello hello'
    assert gzip.decompress(STORED) == make_data(1000)
    assert gzip.decompress(EMPTY) == b''
    assert gzip.decompress(b'') == b''
    assert gzip.decompress(FIELDS) == b'with header fields'
    # members follow each other, with zero padding in between
    assert gzip.decompress(SMALL + b'\0\0' + STORED + EMPTY + SMALL) == \
        b'hello hello hello' + make_data(1000) + b'hello hello hello'


def test_errors():
    eof = 'EOFError: Compressed file ended before the end-of-stream marker was reached'
    assert error(b'xyz') == "BadGzipFile: Not a gzipped file (b'xy')"
    assert error(SMALL + b'x') == "BadGzipFile: Not a gzipped file (b'x')"
    assert error(b'\x1f\x8b\x07' + SMALL[3:]) == 'BadGzipFile: Unknown compression method'
    assert error(SMALL[:5]) == eof
    assert error(SMALL[:15]) == eof
    assert error(BIG[:-4]) == eof
    assert error(SMALL[:-8] + b'\0\0\0\0' + SMALL[-4:]) == 'BadGzipFile: CRC check failed'
    assert error(SMALL[:-4] + b'\x10\0\0\0') == 'BadGzipFile: Incorrect length of data produced'


def test_file():
    path = 'test_mod_gzip.tmp.gz'
    with open(path, 'wb') as f:
        f.write(BIG)
    with gzip.open(path) as g:
        assert g.read() == make_data(60000)
    g = gzip.GzipFile(path)
    assert g.read(7) == make_data(7)
    lines = g.readlines()
    assert b''.join(lines) == make_data(60000)[7:]
    g.close()
    with gzip.open(path, 'rb') as g:
        n = 0
        for line in g:
            n += 1
        assert n == make_data(60000).count(b'\n') + 1

    with open(path, 'wb') as f:
        f.write(SMALL[:-8] + b'\0\0\0\0' + SMALL[-4:])
    try:
        with gzip.open(path) as g:
            g.read()
        assert False
    except gzip.BadGzipFile as e:
        assert str(e) == 'CRC check failed 0x0 != 0xe5f98880', str(e)
    os.remove(path)


def test_all():
    test_decompress()
    test_errors()
    test_file()


if __name__ == '__main__':
    test_all()
