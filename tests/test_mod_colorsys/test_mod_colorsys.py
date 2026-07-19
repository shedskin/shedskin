import colorsys

def fmt_triple(triple):
    res = []
    for val in triple:
        res.append("%.2f" % val)
    return tuple(res)

def test_colorsys():
    assert colorsys.rgb_to_hsv(0.2, 0.4, 0.4) == (0.5, 0.5, 0.4)
    assert colorsys.hsv_to_rgb(0.5, 0.5, 0.4) == (0.2, 0.4, 0.4)

    assert "%.2f" % colorsys.ONE_THIRD == '0.33'
    assert "%.2f" % colorsys.ONE_SIXTH == '0.17'
    assert "%.2f" % colorsys.TWO_THIRD == '0.67'

    assert fmt_triple(colorsys.hls_to_rgb(1.0, 0.5, 0.7)) == ('0.85', '0.15', '0.15')
    assert fmt_triple(colorsys.rgb_to_hls(1.0, 0.5, 0.7)) == ('0.93', '0.75', '1.00')
    assert fmt_triple(colorsys.rgb_to_yiq(1.0, 0.5, 0.7)) == ('0.67', '0.24', '0.17')
    assert fmt_triple(colorsys.hsv_to_rgb(1.0, 0.5, 0.7)) == ('0.70', '0.35', '0.35')
    assert fmt_triple(colorsys.rgb_to_hsv(1.0, 0.5, 0.7)) == ('0.93', '0.50', '1.00')

def test_yiq_roundtrip():
    # Regression test: rgb_to_yiq/yiq_to_rgb must use a mathematically
    # consistent (mutually-inverse) set of constants. Older constants
    # (0.6/-0.28/-0.32 forward, 0.948262/... inverse) do not actually
    # invert each other and drift by ~1e-6 per component on round-trip.
    # See CPython gh-58531 / bpo-14323 "Normalize math precision in
    # RGB/YIQ conversion".
    for r, g, b in [(0.7, 0.2, 0.9), (1.0, 0.5, 0.7), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]:
        y, i, q = colorsys.rgb_to_yiq(r, g, b)
        r2, g2, b2 = colorsys.yiq_to_rgb(y, i, q)
        assert abs(r - r2) < 1e-9
        assert abs(g - g2) < 1e-9
        assert abs(b - b2) < 1e-9

def test_all():
    test_colorsys()
    test_yiq_roundtrip()


if __name__ == "__main__":
    test_all()

