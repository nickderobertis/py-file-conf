import pluggy


def get_plugin_manager() -> pluggy.PluginManager:
    from pyfileconf.plugin import hookspecs, default_hooks

    plm = pluggy.PluginManager("pyfileconf")
    plm.add_hookspecs(hookspecs)
    plm.load_setuptools_entrypoints("pyfileconf")
    plm.register(default_hooks)
    return plm


def reset_plugins():
    from pyfileconf.plugin import manager

    plm = get_plugin_manager()
    manager.plm = plm


def remove_default_plugins():
    from pyfileconf.plugin import manager

    manager.plm.unregister(name='pyfileconf.plugin.default_hooks')