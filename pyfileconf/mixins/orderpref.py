from pyfileconf.logic.userinput import _is_begin_str

class OrderPreferenceMixin:

    @property
    def preferred_position(self):
        return 'begin' if self.prefer_beginning else 'end'

    @preferred_position.setter
    def preferred_position(self, position_str: str):
        self.prefer_beginning = self._is_begin_str(position_str)

    def _is_begin_str(self, begin_str: str) -> bool:
        return _is_begin_str(begin_str)