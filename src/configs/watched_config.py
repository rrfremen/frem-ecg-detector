class WatchedConfig(dict):
    def __init__(self, initial: dict = None):
        self.watchers = {}
        super().__init__()
        if initial:
            self.update(initial)

    def load_config(self, config: dict):
        def to_watched(obj):
            if isinstance(obj, dict):
                return WatchedConfig({k: to_watched(v) for k, v in obj.items()})
            return obj
        self.update(to_watched(config))

    def watch(self, key, callback):
        self.watchers.setdefault(key, []).append(callback)

    def plain_dict(self):
        return {k: v.plain_dict() if isinstance(v, WatchedConfig) else v for k, v in self.items()}

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, WatchedConfig):
            value = WatchedConfig(value)
        old_value = self.get(key)
        super().__setitem__(key, value)
        watchers = getattr(self, 'watchers', {})
        if key in watchers and old_value != value:
            for callback in watchers[key]:
                callback(key, value)

    def update(self, data=None, **kwargs):
        if data:
            for key, value in data.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
