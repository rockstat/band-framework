from .dock import Dock
from .. import (RESULT_OK, RESULT_PONG, BAND_SERVICE, KERNEL_SERVICE,
                settings, pick, logger)

dock = Dock(**settings)

__all__ = ['Dock', 'dock']

