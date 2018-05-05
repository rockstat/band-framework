import sys
from . import settings, start_server


def main():

    """The main routine."""
    # if args is None:
    #     args = sys.argv[1:]

        # print(args)


    start_server(**settings)

if __name__ == '__main__':
    main()


