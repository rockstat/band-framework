import sys
from . import settings, start_server

def main():
    start_server(**settings)

if __name__ == '__main__':
    main()


