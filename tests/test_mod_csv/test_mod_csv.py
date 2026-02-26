import csv
import collections
import os
import os.path

# TODO QUOTE_NOTNULL, QUOTE_STRINGS
# TODO DictReader, DictWriter: iterable fieldnames arg
# TODO test restkey, restval, line_num, extrasaction
# TODO DictReader: skip empty rows/blanks? see __next__
# TODO *.writerows: iterable arg?
# TODO rewrite parser

# TODO Dialect subclassing..?


def _csv_in_out():
    if os.path.exists('testdata'):
        csvfile_in = os.path.join('testdata', 'woef.csv')
        csvfile_out = os.path.join('testdata', 'bla.csv')
    elif os.path.exists('../testdata'):
        csvfile_in = os.path.join('../testdata', 'woef.csv')
        csvfile_out = os.path.join('../testdata', 'bla.csv')
    else:
        csvfile_in = os.path.join('../../testdata', 'woef.csv')
        csvfile_out = os.path.join('../../testdata', 'bla.csv')
    return csvfile_in, csvfile_out


def test_program():
    csvfile_in, csvfile_out = _csv_in_out()

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


def test_dialects():
    csvfile_in, csvfile_out = _csv_in_out()

    dialects = csv.list_dialects()
    assert set(dialects) == set(['excel', 'excel-tab', 'unix'])

    dialect = csv.get_dialect('excel')
    assert dialect.delimiter == ','
    assert dialect.doublequote is True
    assert dialect.escapechar is None
    assert dialect.lineterminator == '\r\n'
    assert dialect.quotechar == '"'
    assert dialect.quoting == 0
    assert dialect.skipinitialspace is False
    assert dialect.strict is False

    dialect = csv.get_dialect('excel-tab')
    assert dialect.delimiter == '\t'
    assert dialect.doublequote is True
    assert dialect.escapechar is None
    assert dialect.lineterminator == '\r\n'
    assert dialect.quotechar == '"'
    assert dialect.quoting == 0
    assert dialect.skipinitialspace is False
    assert dialect.strict is False

    dialect = csv.get_dialect('unix')
    assert dialect.delimiter == ','
    assert dialect.doublequote is True
    assert dialect.escapechar is None
    assert dialect.lineterminator == '\n'
    assert dialect.quotechar == '"'
    assert dialect.quoting == 1
    assert dialect.skipinitialspace is False
    assert dialect.strict is False

    reader = csv.reader(open(csvfile_in), dialect=csv.get_dialect('excel'), delimiter='|')
    assert next(reader) == ['aap', ' noot', ' 18', ' ole']
    assert next(reader) == ['aap', ' noot', ' 19', ' ole2']


def test_register_dialect():
    csvfile_in, csvfile_out = _csv_in_out()

    csv.register_dialect('strict_unix', 'unix', strict=True)
    dialects = csv.list_dialects()
    assert set(dialects) == set(['excel', 'excel-tab', 'unix', 'strict_unix'])

    dialect = csv.get_dialect('strict_unix')
    assert dialect.lineterminator == '\n'
    assert dialect.strict

    csv.unregister_dialect('strict_unix')
    dialects = csv.list_dialects()
    assert set(dialects) == set(['excel', 'excel-tab', 'unix'])


def test_errors():
    csvfile_in, csvfile_out = _csv_in_out()

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), dialect="pindasaus")
    except csv.Error as e:
        error = str(e)
    assert error == 'unknown dialect'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), delimiter='xyz')
    except TypeError as e:
        error = str(e)
    assert error == '"delimiter" must be a 1-character string'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), quotechar='"""')
    except TypeError as e:
        error = str(e)
    assert error == '"quotechar" must be a 1-character string'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), escapechar='hoei')
    except TypeError as e:
        error = str(e)
    assert error == '"escapechar" must be a 1-character string'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), quoting=100)
    except TypeError as e:
        error = str(e)
    assert error == 'bad "quoting" value'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), delimiter="\n")
    except ValueError as e:
        error = str(e)
    assert error == 'bad delimiter value'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), delimiter=":", lineterminator="::")
    except ValueError as e:
        error = str(e)
    assert error == 'bad delimiter or lineterminator value'


    # TODO more cases

    #csv.reader(open(csvfile_out, "w"), delimiter=None) TODO problematic.. more templating? :S


def test_all():
    test_program()
    test_dialects()
    test_register_dialect()
    test_errors()


if __name__ == "__main__":
    test_all()
