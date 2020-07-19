import pluggy
from pyfileconf.plugin import hookspecs, default_hooks

plm = pluggy.PluginManager("pyfileconf")
plm.add_hookspecs(hookspecs)
plm.load_setuptools_entrypoints("eggsample")
plm.register(default_hooks)