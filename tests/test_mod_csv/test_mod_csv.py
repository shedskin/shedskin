import csv
import collections
import os
import os.path

def test_program():
    if os.path.exists('testdata'):
        csvfile_in = os.path.join('testdata', 'woef.csv')
        csvfile_out = os.path.join('testdata', 'bla.csv')
    elif os.path.exists('../testdata'):
        csvfile_in = os.path.join('../testdata', 'woef.csv')
        csvfile_out = os.path.join('../testdata', 'bla.csv')
    else:
        csvfile_in = os.path.join('../../testdata', 'woef.csv')
        csvfile_out = os.path.join('../../testdata', 'bla.csv')

    dialects = csv.list_dialects()
    assert 'excel' in dialects
    assert 'excel-tab' in dialects

    d = collections.defaultdict(list)
    for (a, b, n, l) in csv.reader(open(csvfile_in), delimiter="|"):
        d[a, b].append((int(n), l))
    for a, b in sorted(d, key=lambda t: t[1]):
        hoppa = " ".join([l for (n, l) in sorted(d[a, b], key=lambda t: t[0])])
        hoppa = hoppa.replace("&nbsp;", " ")
    output = open(csvfile_out, "w")
    wr = csv.writer(output, delimiter="|", lineterminator="\n")
    wr.writerow(["aa", "bb", "cc"])
    wr.writerows(2 * [["a", "c", "b"]])
    output.close()

    assert csv.field_size_limit() == 131072

    csv.reader(
        open(csvfile_in),
        dialect="excel",
        delimiter=",",
        quotechar='"',
        lineterminator="\r\n",
        escapechar="\\",
    )
    csv.writer(
        open(csvfile_out, "w"),
        dialect="excel",
        delimiter=",",
        quotechar='"',
        lineterminator="\r\n",
        escapechar="\\",
    )

    bla = open(csvfile_out, "w")
    fieldnames = ["hop", "hap", "ole", "aap"]
    wr2 = csv.DictWriter(
        bla, fieldnames, restval="ah", quoting=csv.QUOTE_ALL, lineterminator="\n"
    )
    rd = csv.DictReader(
        open(csvfile_in), fieldnames, restval="uh", restkey="oh", delimiter="|"
    )
    for d2 in rd:
        # print(sorted(d2.values()))
        wr2.writerow(d2)
        wr2.writerows([d2])
    bla.close()
    rd.fieldnames = fieldnames
    assert rd.fieldnames == ['hop', 'hap', 'ole', 'aap']
    # print(open(csvfile_out).read())

    csv.DictReader(
        open(csvfile_in),
        None,
        dialect="excel",
        delimiter=",",
        quotechar='"',
        lineterminator="",
        escapechar="\\",
    )
    csv.DictWriter(
        open(csvfile_in),
        None,
        dialect="excel",
        delimiter=",",
        quotechar='"',
        lineterminator="",
        escapechar="\\",
    )


def test_all():
    test_program()


if __name__ == "__main__":
    test_all()

