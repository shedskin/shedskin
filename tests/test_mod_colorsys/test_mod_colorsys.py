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

def test_all():
    test_colorsys()


if __name__ == "__main__":
    test_all()

