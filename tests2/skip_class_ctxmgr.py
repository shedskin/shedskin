
class WriteFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None

    def log(self, text):
        self.file.write(text + "\n")

    def __enter__(self):
        self.file = open(self.file_name, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

def test_class_ctx_mgr():
    logfile = "testdata/log.txt"
    with WriteFile(logfile) as f:
        f.log("Log Test 1")
        f.log("Log Test 2")

    with open(logfile) as g:
        lines = g.readlines()
        assert lines[0] == "Log Test 1\n"



def test_all():
    test_class_ctx_mgr()

if __name__ == '__main__':
    test_all()

