class FileSize:
    GB = 1024*1024*1024*1024
    MB = 1024*1024*1024
    KB = 1024*1024

    @staticmethod
    def get_gb(b: int):
        return b / FileSize.GB

    @staticmethod
    def get_mb(b: int):
        return b / FileSize.MB

    @staticmethod
    def get_kb(b: int):
        return b / FileSize.KB
