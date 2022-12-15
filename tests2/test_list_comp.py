

def test_list_comp():
    assert [0 for s in ["hah"]] == [0]
    assert [bah.upper() for bah in ("hah", "bah")] == ['HAH', 'BAH']
    assert [0 for (str, bah) in [("hah", "bah")]] == [0]


if __name__ == '__main__':
    test_list_comp()
