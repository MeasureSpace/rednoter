class RednoterError(Exception):
    pass

class DownloadError(RednoterError):
    pass

class TranscriptionError(RednoterError):
    pass

class ConfigurationError(RednoterError):
    pass
