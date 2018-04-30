# __package__ = __name__
from .adome import *
dome = Dome()

from .lib import *
from .rpc import *
from .server import *

settings = completely_config()
print(settings)

__all__ = (lib.__all__ + rpc.__all__ +
           adome.__all__ + server.__all__) + ['dome']

if settings.is_master:
    from .director import *
    __all__ += director.__all__
else:
    from service import *
    __all__ = + service.__all__
