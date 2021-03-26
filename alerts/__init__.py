
alerts = {}

from . import total_volume
alerts['total_volume'] = total_volume.TotalVolume

from .alert import *
