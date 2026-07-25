import base64
import binascii


def test_basic():
    input_bytes = bytes(range(256))

    e = base64.b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
    assert base64.b64decode(e) == input_bytes

    e = base64.standard_b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
    assert base64.standard_b64decode(e) == input_bytes

    e = base64.urlsafe_b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w=='
    assert base64.urlsafe_b64decode(e) == input_bytes


def test_altchars():
    input_bytes = bytes(range(256))

    a1 = base64.b64encode(input_bytes)
    assert a1 == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='

    a2 = base64.b64encode(input_bytes, altchars=b'*?')
    assert a2 == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0*P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn*AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq*wsbKztLW2t7i5uru8vb6?wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t?g4eLj5OXm5*jp6uvs7e7v8PHy8?T19vf4*fr7?P3*?w=='

    assert base64.b64decode(a1) == input_bytes
    assert base64.b64decode(a2, altchars=b'*?') == input_bytes


def test_name():
    assert base64.__name__ == 'base64'


def test_validate():
    good = base64.b64encode(b'Hello!')
    assert base64.b64decode(good, validate=True) == b'Hello!'

    # non-alphabet characters raise when validate=True ...
    bad = b'SGVsbG8h@#$%'
    ok = False
    try:
        base64.b64decode(bad, validate=True)
    except binascii.Error:
        ok = True
    assert ok

    # ... but are tolerated when validate=False (the default)
    assert base64.b64decode(bad, validate=False) == b'Hello!'
    assert base64.b64decode(bad) == b'Hello!'


def test_b16():
    input_bytes = bytes(range(256))
    e = base64.b16encode(input_bytes)
    assert e == binascii.hexlify(input_bytes).upper()
    assert base64.b16decode(e) == input_bytes
    assert base64.b16decode(e.lower(), casefold=True) == input_bytes

    ok = False
    try:
        base64.b16decode(e.lower())
    except binascii.Error:
        ok = True
    assert ok


# regression test: altchars must be exactly 2 bytes, like CPython's
# `assert len(altchars) == 2, repr(altchars)` in base64.py. Without this
# check, a too-short altchars caused an out-of-bounds vector read and a
# too-long one was silently (and incorrectly) truncated.
#
# Note: CPython's base64.py enforces this with a plain `assert`, which
# raises AssertionError (and can be compiled away with -O); shedskin
# raises ValueError instead, which is deliberate and more robust. Both
# are accepted here so this test runs the same under CPython and
# shedskin.
def test_altchars_bad_length():
    for bad in (b'', b'-', b'-_-'):
        ok = False
        try:
            base64.b64encode(b'hello world', altchars=bad)
        except (AssertionError, ValueError):
            ok = True
        assert ok

        ok = False
        try:
            base64.b64decode(b'aGVsbG8gd29ybGQ=', altchars=bad)
        except (AssertionError, ValueError):
            ok = True
        assert ok


# regression test: b64decode must reject truncated/incorrectly padded
# input instead of silently returning wrong (truncated or fabricated)
# bytes. Mirrors CPython's binascii.Error('Incorrect padding') and
# binascii.Error('Invalid base64-encoded string: ...') behavior.
def test_decode_bad_padding():
    # b'QQ': 2 chars, no padding at all
    # b'QQ=': 2 chars, only one pad (needs two)
    # b'AA': 2 chars decode to < 1 full byte
    # b'A': single dangling char, never valid
    # b'A=': single dangling char + one pad
    for bad in (b'QQ', b'QQ=', b'AA', b'A', b'A='):
        ok = False
        try:
            base64.b64decode(bad)
        except binascii.Error:
            ok = True
        assert ok

    # well-formed padding must still decode correctly (regression check
    # for the fix itself: an earlier version of this fix broke this case)
    assert base64.b64decode(b'QQ==') == b'A'
    assert base64.b64decode(b'QUJD') == b'ABC'
    assert base64.b64decode(b'QUJ=') == b'AB'
    assert base64.b64decode(b'====') == b''
    assert base64.b64decode(b'') == b''


# regression test for a global-buffer-overflow (OOB read past the
# empty string literal used to preallocate output buffers) that
# AddressSanitizer catches on completely ordinary encode/decode calls,
# with no altchars or adversarial input needed.
def test_asan_regression():
    for n in (0, 1, 2, 3, 4, 5, 16, 45, 60, 61, 62, 63, 64, 100, 1000):
        data = bytes((i * 37) % 256 for i in range(n))
        e = base64.b64encode(data)
        assert base64.b64decode(e) == data
        h = base64.b16encode(data)
        assert base64.b16decode(h) == data


def test_all():
    test_basic()
    test_altchars()
    test_altchars_bad_length()
    test_name()
    test_validate()
    test_decode_bad_padding()
    test_b16()
    test_asan_regression()


if __name__ == '__main__':
    test_all()
