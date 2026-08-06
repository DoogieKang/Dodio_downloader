# PyInstaller 런타임 훅: numpy 2.x에서 제거된 속성을 복원해 openpyxl 호환성 유지
try:
    import numpy
    if not hasattr(numpy, 'short'):
        numpy.short = numpy.int16
    if not hasattr(numpy, 'long'):
        numpy.long = numpy.int_
    if not hasattr(numpy, 'bool'):
        numpy.bool = numpy.bool_
    if not hasattr(numpy, 'int'):
        numpy.int = numpy.int_
    if not hasattr(numpy, 'float'):
        numpy.float = numpy.float64
    if not hasattr(numpy, 'complex'):
        numpy.complex = numpy.complex128
    if not hasattr(numpy, 'object'):
        numpy.object = object
    if not hasattr(numpy, 'str'):
        numpy.str = numpy.str_
except ImportError:
    pass
