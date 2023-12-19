import struct


def test_unpack():
    a, = struct.unpack("h", b'\x00\n')
    assert a == 2560

    a, b, c = struct.unpack('>bhl', b'\x01\x00\x02\x00\x00\x00\x03')
    assert (a, b, c) == (1, 2, 3)

    a, b, c, d, e, f, g, h = struct.unpack("<BBHHHII16s", 32 * b"0")
    assert (a, b, c, d, e, f, g) == (48, 48, 12336, 12336, 12336, 808464432, 808464432)
    assert h == b'0000000000000000'

    header_format = "<32s2BHHH24s"
    h, a, b, c, d, e, i = struct.unpack(header_format, 64 * b"0")
    assert h == b'00000000000000000000000000000000'
    assert (a, b, c, d, e) == (48, 48, 12336, 12336, 12336)
    assert i == b'000000000000000000000000'

    version = [0, 0]
    (
         magic,
         version[0],
         version[1],
         max_files,
         cur_files,
         reserved,
         user_description,
    ) = struct.unpack(header_format, 64 * b"0")
    assert magic == b'00000000000000000000000000000000'
    assert version == [48, 48]
    assert cur_files == 12336


def test_H():
    assert struct.pack(">h", 10) == b'\x00\n'

    packer = struct.pack("HH", 1, 2)
    assert packer == b'\x01\x00\x02\x00'
    (p0, p1) = struct.unpack("HH", packer)
    assert p0 == 1
    assert p1 == 2


def test_d():
    packer = struct.pack("d", 949.1)
    d, = struct.unpack("d", packer)
    assert d == 949.1


def test_unpack_issue():
    s = struct.pack('>I', 12000)
    n, = struct.unpack('>I', s)
    assert n == 12000

    s = struct.pack('>i', -12000)
    n, = struct.unpack('>i', s)
    assert n == -12000


def test_unpack_from():
    data = b'\xf0\x04\x00\x00\x01\x02'
    n, = struct.unpack_from('<I', data)
    assert n == 1264


def test_pack_into():
    bla = bytearray(10)
    struct.pack_into('<hh', bla, 4, 17, 18)
    a, b = struct.unpack_from('<hh', bla, 4)
    assert a == 17 and b == 18


def test_calcsize():
    assert struct.calcsize('>bhl') == 7
    assert struct.calcsize("HH") == 4
    header_format = "<32s2BHHH24s"
    assert struct.calcsize(header_format) == 64

def test_all():
    test_unpack()
    test_unpack_from()
    test_unpack_issue()
    test_H()
    test_d()
    test_pack_into()
    test_calcsize()

if __name__ == '__main__':
    test_all()


# packer = struct.pack("!c3L2b3p", b"\xd5", 39, 77, 77, 55, 50, b"\xf3\x8bq")
# print(repr(packer))
# print(struct.calcsize("!c3L2b3p"))
# (
#     p1_0,
#     p1_1,
#     p1_2,
#     p1_3,
#     p1_4,
#     p1_5,
#     p1_6,
# ) = struct.unpack("!c3L2b3p", packer)
# print(
#     repr(p1_0),
#     repr(p1_1),
#     repr(p1_2),
#     repr(p1_3),
#     repr(p1_4),
#     repr(p1_5),
#     repr(p1_6),
# )
# print()
# packer = struct.pack("!q2i2Q3H", 91, 62, 118, 45, 113, 72, 117, 92)
# print(repr(packer))
# print(struct.calcsize("!q2i2Q3H"))
# (
#     p2_0,
#     p2_1,
#     p2_2,
#     p2_3,
#     p2_4,
#     p2_5,
#     p2_6,
#     p2_7,
# ) = struct.unpack("!q2i2Q3H", packer)
# print(
#     repr(p2_0),
#     repr(p2_1),
#     repr(p2_2),
#     repr(p2_3),
#     repr(p2_4),
#     repr(p2_5),
#     repr(p2_6),
#     repr(p2_7),
# )
# print()
# packer = struct.pack("=2Ib3L3s", 30, 3, 65, 23, 114, 101, b"\xc3\xcaZ")
# print(repr(packer))
# print(struct.calcsize("=2Ib3L3s"))
# (
#     p3_0,
#     p3_1,
#     p3_2,
#     p3_3,
#     p3_4,
#     p3_5,
#     p3_6,
# ) = struct.unpack("=2Ib3L3s", packer)
# print(
#     repr(p3_0),
#     repr(p3_1),
#     repr(p3_2),
#     repr(p3_3),
#     repr(p3_4),
#     repr(p3_5),
#     repr(p3_6),
# )
# print()
# packer = struct.pack("!3?2l", False, False, True, 75, 39)
# print(repr(packer))
# print(struct.calcsize("!3?2l"))
# (
#     p4_0,
#     p4_1,
#     p4_2,
#     p4_3,
#     p4_4,
# ) = struct.unpack("!3?2l", packer)
# print(
#     repr(p4_0),
#     repr(p4_1),
#     repr(p4_2),
#     repr(p4_3),
#     repr(p4_4),
# )
# print()
# packer = struct.pack("3B3x2b", 26, 112, 54, 86, 10)
# print(repr(packer))
# print(struct.calcsize("3B3x2b"))
# (
#     p5_0,
#     p5_1,
#     p5_2,
#     p5_3,
#     p5_4,
# ) = struct.unpack("3B3x2b", packer)
# print(
#     repr(p5_0),
#     repr(p5_1),
#     repr(p5_2),
#     repr(p5_3),
#     repr(p5_4),
# )
# print()
# packer = struct.pack("@3H3qs", 67, 14, 69, 12, 66, 91, b"v")
# print(repr(packer))
# print(struct.calcsize("@3H3qs"))
# (
#     p6_0,
#     p6_1,
#     p6_2,
#     p6_3,
#     p6_4,
#     p6_5,
#     p6_6,
# ) = struct.unpack("@3H3qs", packer)
# print(
#     repr(p6_0),
#     repr(p6_1),
#     repr(p6_2),
#     repr(p6_3),
#     repr(p6_4),
#     repr(p6_5),
#     repr(p6_6),
# )
# print()
# packer = struct.pack("I2qc2p", 50, 50, 15, b"\xd9", b"\xb1\x06")
# print(repr(packer))
# print(struct.calcsize("I2qc2p"))
# (
#     p7_0,
#     p7_1,
#     p7_2,
#     p7_3,
#     p7_4,
# ) = struct.unpack("I2qc2p", packer)
# print(
#     repr(p7_0),
#     repr(p7_1),
#     repr(p7_2),
#     repr(p7_3),
#     repr(p7_4),
# )
# print()
# packer = struct.pack("b2x2s", 77, b"\xa5~")
# print(repr(packer))
# print(struct.calcsize("b2x2s"))
# (
#     p8_0,
#     p8_1,
# ) = struct.unpack("b2x2s", packer)
# print(
#     repr(p8_0),
#     repr(p8_1),
# )
# print()
# packer = struct.pack("Ip3si", 60, b"-", b"t\xf5\x10", 9)
# print(repr(packer))
# print(struct.calcsize("Ip3si"))
# (
#     p9_0,
#     p9_1,
#     p9_2,
#     p9_3,
# ) = struct.unpack("Ip3si", packer)
# print(
#     repr(p9_0),
#     repr(p9_1),
#     repr(p9_2),
#     repr(p9_3),
# )
# print()
# packer = struct.pack("<ibBx", 82, 108, 61)
# print(repr(packer))
# print(struct.calcsize("<ibBx"))
# (
#     p10_0,
#     p10_1,
#     p10_2,
# ) = struct.unpack("<ibBx", packer)
# print(
#     repr(p10_0),
#     repr(p10_1),
#     repr(p10_2),
# )
# print()
# packer = struct.pack("!c3q2b3d", b"\xd5", 39, 77, 77, 55, 50, 949.0, 544.0, 444.0)
# print(repr(packer))
# print(struct.calcsize("!c3q2b3d"))
# (
#     p11_0,
#     p11_1,
#     p11_2,
#     p11_3,
#     p11_4,
#     p11_5,
#     p11_6,
#     p11_7,
#     p11_8,
# ) = struct.unpack("!c3q2b3d", packer)
# print(
#     repr(p11_0),
#     repr(p11_1),
#     repr(p11_2),
#     repr(p11_3),
#     repr(p11_4),
#     repr(p11_5),
#     repr(p11_6),
#     repr(p11_7),
#     repr(p11_8),
# )
# print()
# packer = struct.pack("l2Qc2d", 50, 50, 15, b"\xd9", 692.0, 24.0)
# print(repr(packer))
# print(struct.calcsize("l2Qc2d"))
# (
#     p12_0,
#     p12_1,
#     p12_2,
#     p12_3,
#     p12_4,
#     p12_5,
# ) = struct.unpack("l2Qc2d", packer)
# print(
#     repr(p12_0),
#     repr(p12_1),
#     repr(p12_2),
#     repr(p12_3),
#     repr(p12_4),
#     repr(p12_5),
# )
# print()
# packer = struct.pack("<0p0I", b"")
# print(repr(packer))
# print(struct.calcsize("<0p0I"))
# packer = struct.pack("<3Q0s2B1i", 64, 117, 20, b"", 48, 38, 50)
# print(repr(packer))
# print(struct.calcsize("<3Q0s2B1i"))
# (
#     p14_0,
#     p14_1,
#     p14_2,
#     p14_3,
#     p14_4,
#     p14_5,
#     p14_6,
# ) = struct.unpack("<3Q0s2B1i", packer)
# print(
#     repr(p14_0),
#     repr(p14_1),
#     repr(p14_2),
#     repr(p14_3),
#     repr(p14_4),
#     repr(p14_5),
#     repr(p14_6),
# )
# print()
# packer = struct.pack("<0L2f0p1x", 682.0, 307.0, b"")
# print(repr(packer))
# print(struct.calcsize("<0L2f0p1x"))
# packer = struct.pack("=s", b"\xe6\xc1\xdc\xb4y9\xa9")
# print(repr(packer))
# print(struct.calcsize("=s"))
# (p16_0,) = struct.unpack("=s", packer)
# print(
#     repr(p16_0),
# )
# print()
# packer = struct.pack(
#     "<3c3i3l2p", b"\x84", b"\xb7", b"A", 90, 51, 127, 18, 56, 3, b"\x82"
# )
# print(repr(packer))
# print(struct.calcsize("<3c3i3l2p"))
# (
#     p17_0,
#     p17_1,
#     p17_2,
#     p17_3,
#     p17_4,
#     p17_5,
#     p17_6,
#     p17_7,
#     p17_8,
#     p17_9,
# ) = struct.unpack("<3c3i3l2p", packer)
# print(
#     repr(p17_0),
#     repr(p17_1),
#     repr(p17_2),
#     repr(p17_3),
#     repr(p17_4),
#     repr(p17_5),
#     repr(p17_6),
#     repr(p17_7),
#     repr(p17_8),
#     repr(p17_9),
# )
# print()
# packer = struct.pack("<0p3??", b"\x85", False, 2, 0, b"huh")
# print(repr(packer))
# print(struct.calcsize("<0p3??"))
# packer = struct.pack("!c3pp1q", b"\xe4", b"1", b"\xfeE\x9f\xdf`\x969\xdb", 40)
# print(repr(packer))
# print(struct.calcsize("!c3pp1q"))
# (
#     p19_0,
#     p19_1,
#     p19_2,
#     p19_3,
# ) = struct.unpack("!c3pp1q", packer)
# print(
#     repr(p19_0),
#     repr(p19_1),
#     repr(p19_2),
#     repr(p19_3),
# )
# print()
# packer = struct.pack("!3s", b"")
# print(repr(packer))
# print(struct.calcsize("!3s"))
# (p20_0,) = struct.unpack("!3s", packer)
# print(
#     repr(p20_0),
# )
# print()
# packer = struct.pack("@0q3x0p0d", b"\x13\xe5\xb4\x98.\xff")
# print(repr(packer))
# print(struct.calcsize("@0q3x0p0d"))
# packer = struct.pack("0p2I?H", b"\xe7\xa3\xd2", 426, 403, b"hoi", 85)
# print(repr(packer))
# print(struct.calcsize("0p2I?H"))
# packer = struct.pack(">0i0p3p2x", b"g\xb0\x0c\x02\x89\xd3\xaf", b"\xfdK\xb4\xb1\xf6l")
# print(repr(packer))
# print(struct.calcsize(">0i0p3p2x"))
# packer = struct.pack(">b0p2s", 110, b"\x1d", b"")
# print(repr(packer))
# print(struct.calcsize(">b0p2s"))
# packer = struct.pack("@2f0p3p1L", 531.0, 469.0, b"1k\x1a\x8c\xfd\xc0u\xdf", b"", 60)
# print(repr(packer))
# print(struct.calcsize("@2f0p3p1L"))
# try:
#     s = struct.pack("h", 18.18)
#     print(repr(s))
#     (dwah,) = struct.unpack("h", s)
#     print(dwah)
#     s = struct.pack("h", "19")
#     print(repr(s))
#     (dwah,) = struct.unpack("h", s)
#     print(dwah)
#     s = struct.pack("h", True)
#     print(repr(s))
#     (dwah,) = struct.unpack("h", s)
#     print(dwah)
# except Exception as messg:
#     print("baaah")
# try:
#     s = struct.pack("fd", 17, 18)
#     print(repr(s))
#     dwad, ewad = struct.unpack("fd", s)
#     print(dwad, ewad)
#     s = struct.pack("fd", "oi", 18)
# except Exception:
#     print("oopsie")
# try:
#     raise struct.error("butkus")
# except struct.error as e:
#     print(e)
# (booll,) = struct.unpack("?", b"\x02")
# print(booll)
# print(repr(struct.pack("p", 300 * b"x")))


# s = struct.pack("h", -12)
# (xx,) = struct.unpack("h", s)
# print(xx)
# s = struct.pack("i", -13)
# (xx,) = struct.unpack("i", s)
# print(xx)
# s = struct.pack("l", -14)
# (xx,) = struct.unpack("l", s)
# print(xx)


# s = struct.pack("B", True)
# print(s)
