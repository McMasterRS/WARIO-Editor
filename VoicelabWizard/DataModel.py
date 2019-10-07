# Accessor class for settings

class SettingsDataModel():
    def __init__(self, default_settings):
        self.default_settings = default_settings


class SettingData():
    def __init__(self, default, fn_setter=None):
        self.data = default
        self.type = type(default)
        self.fn_setter = fn_setter
    
    @property
    def value(self):
        return self.data

    @value.setter
    def value(self, data):
        self.data = data