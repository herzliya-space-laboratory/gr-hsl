INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_HSL hsl)

FIND_PATH(
    HSL_INCLUDE_DIRS
    NAMES hsl/api.h
    HINTS $ENV{HSL_DIR}/include
        ${PC_HSL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    HSL_LIBRARIES
    NAMES gnuradio-hsl
    HINTS $ENV{HSL_DIR}/lib
        ${PC_HSL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(HSL DEFAULT_MSG HSL_LIBRARIES HSL_INCLUDE_DIRS)
MARK_AS_ADVANCED(HSL_LIBRARIES HSL_INCLUDE_DIRS)

