# winner of code contest at pycontest.net

def test_all():
    seven_seg=lambda z:''.join(''.join(' _   |_|_ _| |'[ord("'\xa5\x8f\xb1\xdb\xad\xbdi\x03K\x9f'"[int(a)])%u:][:3]for a in z)+"\n"for u in(3,14,10))

    s = seven_seg([1,2,3,4,5,6,7,8,9,10])
    print(s)

    assert s == \
    (
       ' _     _  _     _  _  _  _  _ \n'
       '| |  | _| _||_||_ |_   ||_||_|\n'
       '|_|  ||_  _|  | _||_|  ||_| _|\n'
    )


if __name__ == '__main__':
    test_all()
