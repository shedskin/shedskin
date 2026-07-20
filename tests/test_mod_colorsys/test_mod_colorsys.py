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

def test_hsv_hue_sextants():
    # Regression test: hsv_to_rgb splits the hue circle into six sextants via
    # i = int(h*6.0), and rgb_to_hls/rgb_to_hsv/_v normalize hue via
    # mods(h/6.0, 1.0). Both of these exercise the boundary between each
    # sextant; pin known-good values at and near every boundary (h = 0,
    # 1/6, 2/6, 3/6, 4/6, 5/6, and just past 1.0 to check wraparound).
    cases = [
        (0.0 / 6, ('1.00', '0.00', '0.00')),
        (1.0 / 6, ('1.00', '1.00', '0.00')),
        (2.0 / 6, ('0.00', '1.00', '0.00')),
        (3.0 / 6, ('0.00', '1.00', '1.00')),
        (4.0 / 6, ('0.00', '0.00', '1.00')),
        (5.0 / 6, ('1.00', '0.00', '1.00')),
        (1.0, ('1.00', '0.00', '0.00')),
    ]
    for h, expected in cases:
        assert fmt_triple(colorsys.hsv_to_rgb(h, 1.0, 1.0)) == expected

    for h in (0.0, 1.0 / 6, 2.0 / 6, 3.0 / 6, 4.0 / 6, 5.0 / 6, 1.0):
        r, g, b = colorsys.hsv_to_rgb(h, 0.6, 0.8)
        h2, s2, v2 = colorsys.rgb_to_hsv(r, g, b)
        r2, g2, b2 = colorsys.hsv_to_rgb(h2, s2, v2)
        assert fmt_triple((r, g, b)) == fmt_triple((r2, g2, b2))

def test_all():
    test_colorsys()
    test_yiq_roundtrip()
    test_hsv_hue_sextants()


if __name__ == "__main__":
    test_all()

