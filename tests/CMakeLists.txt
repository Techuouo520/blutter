cmake_minimum_required(VERSION 3.20)
project(blutter_regression_tests LANGUAGES CXX)
enable_testing()

# Exercise the production classification helper without a Dart VM or APK.
# Fail configuration if its boundaries change rather than testing a stale copy.
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/../blutter/src/CodeAnalyzer_arm64.cpp")
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/../blutter/src/CodeAnalyzer_arm64.cpp" analyzer)
string(FIND "${analyzer}" "static ArrayOp getArrayOp(" helper_start)
string(FIND "${analyzer}" "std::unique_ptr<ILInstr> FunctionAnalyzer::processLoadStore(" helper_end)
if(helper_start LESS 0 OR helper_end LESS helper_start)
    message(FATAL_ERROR "Array helper boundaries changed; update the regression harness")
endif()
math(EXPR helper_length "${helper_end} - ${helper_start}")
string(SUBSTRING "${analyzer}" ${helper_start} ${helper_length} ARRAY_HELPER)
string(REGEX MATCH "const int32_t payload_offset = arrayOp.arrType == ArrayOp::List[^;]+;[^;]+;" ARRAY_INDEX "${analyzer}")
if(NOT ARRAY_INDEX)
    message(FATAL_ERROR "Array index expression changed; update the regression harness")
endif()
configure_file(array_ops.cpp.in array_ops.cpp @ONLY)

foreach(compressed IN ITEMS 0 1)
    set(target "array_ops_${compressed}")
    add_executable(${target} "${CMAKE_CURRENT_BINARY_DIR}/array_ops.cpp")
    target_compile_features(${target} PRIVATE cxx_std_17)
    target_compile_definitions(${target} PRIVATE TEST_COMPRESSED=${compressed})
    add_test(NAME ${target} COMMAND ${target})
endforeach()
