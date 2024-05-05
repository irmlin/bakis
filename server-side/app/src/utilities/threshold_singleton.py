


# class ThresholdSingleton:
#     __instance = None
#     __value = None
#
#     def __new__(cls):
#         if cls.__instance is None:
#             cls.__instance = super(ThresholdSingleton, cls).__new__(cls)
#         return cls.__instance
#
#     @classmethod
#     def get(cls):
#         print('getting ', cls.__value)
#         return cls.__value
#
#     @classmethod
#     def set(cls, value: float):
#         print('set to', value)
#         cls.__value = value

thr = None
