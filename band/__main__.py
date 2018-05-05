import sys
from . import settings, start_server
from . import director


def main():
    start_server(**settings)

if __name__ == '__main__':
    main()


