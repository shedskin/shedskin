import csv
import collections
import os
import os.path

# TODO QUOTE_NOTNULL, QUOTE_STRINGS
# TODO test restkey, restval, extrasaction
# TODO DictReader: skip empty rows/blanks? see __next__
# TODO rewrite parser
# TODO check QUOTE_NONNUMERIC restriction
# TODO NOTSET/None differences
# TODO check reader/writer attrs

# TODO newline='' to fix lineterminators for excel
# TODO Dialect subclassing..?


def _csv_path(name):
    if os.path.exists('testdata'):
        name = os.path.join('testdata', name)
    elif os.path.exists('../testdata'):
        name = os.path.join('../testdata', name)
    else:
        name = os.path.join('../../testdata', name)
    return name


def test_program():
    csvfile_in = _csv_path('woef.csv')
    csvfile_out = _csv_path('bla.csv')

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
    csvfile_in = _csv_path('woef.csv')
    csvfile_out = _csv_path('bla.csv')

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
    csvfile_in = _csv_path('woef.csv')
    csvfile_out = _csv_path('bla.csv')

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
    csvfile_out = _csv_path('bla.csv')

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
        csv.reader(open(csvfile_out, "w"), delimiter="\n") # illegal char
    except ValueError as e:
        error = str(e)
    assert error == 'bad delimiter value'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), delimiter=":", lineterminator="::") # delimiter in lineterminator
    except ValueError as e:
        error = str(e)
    assert error == 'bad delimiter or lineterminator value'

    error = ''
    try:
        csv.reader(open(csvfile_out, "w"), delimiter="?", quotechar="?")  # same chars
    except ValueError as e:
        error = str(e)
    assert error == 'bad delimiter or quotechar value'

    # TODO more cases

    #csv.reader(open(csvfile_out, "w"), delimiter=None) TODO problematic.. more templating? :S


def test_excel():
    path = _csv_path('excel.csv')

    # normal variant
    reader = csv.reader(open(path))
    assert reader.line_num == 0
    data = list(reader)
    assert reader.line_num == 3

    assert data == [
        ['aap', 'bert', 'frits'],
        ['hoi', '  hop', '18.8'],
        ['hoi2', 'a, b, c', '17'],
    ]

    with open('excel_out.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    assert open(path).read() == open('excel_out.csv').read()  # TODO newline=''

    # dict variant
    dict_reader = csv.DictReader(open(path), fieldnames=['a', 'b', 'c'])  # override header
    assert dict_reader.line_num == 0
    next(dict_reader)
    assert dict_reader.line_num == 1
    rows = list(dict_reader)
    assert dict_reader.line_num == 3
    assert rows == [
        {'a': 'hoi', 'b': '  hop', 'c': '18.8'},
        {'a': 'hoi2', 'b': 'a, b, c', 'c': '17'}
    ]

    dict_reader = csv.DictReader(open(path))
    rows = list(dict_reader)
    assert rows == [
        {'aap': 'hoi', 'bert': '  hop', 'frits': '18.8'},
        {'aap': 'hoi2', 'bert': 'a, b, c', 'frits': '17'}
    ]

    with open('excel_out2.csv', 'w') as f:
        dict_writer = csv.DictWriter(f, fieldnames=iter(['aap', 'bert', 'frits']))  # iterable fieldnames
        dict_writer.writeheader()
        dict_writer.writerows(iter(rows))  # iterable rows

    assert open(path).read() == open('excel_out2.csv').read()  # TODO newline=''


def test_all():
    test_program()
    test_dialects()
    test_register_dialect()
    test_errors()
    test_excel()


if __name__ == "__main__":
    test_all()
