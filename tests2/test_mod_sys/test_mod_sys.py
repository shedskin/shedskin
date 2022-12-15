import sys

def test_sys():
    assert len(sys.argv) > 0
    # assert sys.argv[0] == 'test_mod_sys.py'
    # assert sys.argv[1:] == []

if __name__ == '__main__':
    test_sys()
