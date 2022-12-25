debug = True


class Debug:
    def debug(self, msg):
        if debug:
            return(msg)


def test_case_1():
    assert Debug().debug("debug") == "debug"



    





def test_all():
    test_case_1()

if __name__ == '__main__':
    test_all()