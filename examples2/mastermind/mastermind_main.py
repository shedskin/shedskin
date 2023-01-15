try:
    from mm import mastermind
except ImportError:
    import mastermind
print(mastermind)

""" copyright Sean McCarthy, license GPL v2 or later """

def main():
    mastermind.main()

if __name__=='__main__':
    main()
