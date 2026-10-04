# Regression tests

## Native array tests (no Dart SDK or APK required)

```powershell
cmake -S tests -B build\regression-tests
cmake --build build\regression-tests --config Release
ctest --test-dir build\regression-tests -C Release --output-on-failure
```

The CMake project extracts `getArrayOp` and the fixed-offset index expression
from the production analyzer. Minimal instruction and VM-layout fixtures test
both pointer widths, List vs TypedData classification, element indices,
load/store direction, and rejected instructions. This is a focused unit test,
not a replacement for analyzing a real snapshot.

## Python tests

```powershell
python -m unittest discover -s tests -v
```

Snapshot-hash tests use only the standard library and temporary source fixtures.
Directory tests use `BLUTTER_BIN`, or the newest `blutter_*` executable in `bin`.
On Windows, DLLs are excluded and the POSIX permission test is skipped.

For array integration tests, also set `BLUTTER_TEST_LIBAPP` to an Android ARM64
compressed-pointer `libapp.so` matching the executable's Dart version. Tests
skip when that fixture is absent; an analysis failure with a supplied fixture
is a failure, not a skip.
