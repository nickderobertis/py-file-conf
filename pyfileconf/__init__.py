
"""
Flow Manager is a Python framework for flow-based programming and managing configuration. To use it, you register
your main functions, and config files are created automatically for them. It provides a way to run these functions
individually, in a list, in sections, or a combination thereof. Configuration has multiple layers, with the defaults
for the function being the lowest level config, which then gets overrided by project config, which gets overrided by
the config file, and finally by any local config updates in a script.
"""

from pyfileconf.main import PipelineManager
from pyfileconf.selector.models.selector import Selector
