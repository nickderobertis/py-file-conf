
"""
py-file-conf is a Python framework for flow-based programming and managing configuration. To use it, you register
your main functions and classes, and config files are created automatically for them. It provides a way to run these functions
individually, in a list, in sections, or a combination thereof. Configuration can be 
dynamically updated, enabling powerful scripting.
"""

from pyfileconf.main import PipelineManager
from pyfileconf.selector.models.selector import Selector
