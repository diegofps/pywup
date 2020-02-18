./scheduled.sh SCHEDULED_WISARD_CPU_23 cpu 23 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CPU_23 cpu 23 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CPU_23 cpu 23 kcf ; sleep 60

./scheduled.sh SCHEDULED_WISARD_CPUCSD_23 cpu_csd 23 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CPUCSD_23 cpu_csd 23 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CPUCSD_23 cpu_csd 23 kcf ; sleep 60

./scheduled.sh SCHEDULED_WISARD_CSD_23 csd 23 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CSD_23 csd 23 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CSD_23 csd 23 kcf ; sleep 60

--------------------------------------------------------------------------------

./scheduled.sh SCHEDULED_WISARD_CPU_100 cpu 100 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CPU_100 cpu 100 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CPU_100 cpu 100 kcf ; sleep 60

./scheduled.sh SCHEDULED_WISARD_CPUCSD_100 cpu_csd 100 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CPUCSD_100 cpu_csd 100 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CPUCSD_100 cpu_csd 100 kcf ; sleep 60

./scheduled.sh SCHEDULED_WISARD_CSD_100 csd 100 wisard ; sleep 60 ; \
./scheduled.sh SCHEDULED_MOSSE_CSD_100 csd 100 mosse ; sleep 60 ; \
./scheduled.sh SCHEDULED_KCF_CSD_100 csd 100 kcf ; sleep 60

--------------------------------------------------------------------------------


Ele parece ser todo implementado em CPP e ter wrappers para várias linguagens (Java, Python, Ruby, R, RUST, GO, C#, C, Javascript, Go, etc) 
Consegui instalar as bibliotecas precompiladas e executar um exemplo pequeno

https://www.kdnuggets.com/2017/02/apache-arrow-parquet-columnar-data.html
https://github.com/apache/arrow
https://github.com/apache/arrow/tree/master/cpp/src/arrow
https://arrow.apache.org/install/
https://arrow.apache.org/docs/python/numpy.html
https://arrow.apache.org/docs/developers/cpp.html#building
https://github.com/ninja-build/ninja/wiki/Pre-built-Ninja-packages
https://stackoverflow.com/questions/56472727/difference-between-apache-parquet-and-arrow
https://github.com/apache/arrow/issues/1125
https://issues.apache.org/jira/browse/ARROW-5382?src=confmacro
https://gist.github.com/heavyinfo/04e1326bb9bed9cecb19c2d603c8d521

export PYARROW_WITH_FLIGHT=1
export PYARROW_WITH_GANDIVA=1
export PYARROW_WITH_ORC=1
export PYARROW_WITH_PARQUET=1
export PYARROW_WITH_PLASMA=1

--------------------------------------------------------------------------------

cmake .. -DARROW_PYTHON=ON -DARROW_BUILD_EXAMPLES=ON -DARROW_BUILD_BENCHMARKS=ON \
    -DARROW_BUILD_BENCHMARKS_REFERENCE=ON -DARROW_BUILD_UTILITIES=ON -DARROW_PARQUET=ON \
    -DARROW_WITH_ZLIB=ON -DPARQUET_BUILD_EXECUTABLES=ON -DPARQUET_BUILD_EXAMPLES=ON \
    -DARROW_FLIGHT=ON -DARROW_WITH_BZ2=ON

cmake .. \
      -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
      -DCMAKE_INSTALL_LIBDIR=lib  \
      -DARROW_FLIGHT=ON \
      -DARROW_GANDIVA=ON  \
      -DARROW_ORC=ON  \
      -DARROW_CUDA=ON \
      -DARROW_WITH_BZ2=ON \
      -DARROW_WITH_ZLIB=ON  \
      -DARROW_WITH_ZSTD=ON  \
      -DARROW_WITH_LZ4=ON \
      -DARROW_WITH_SNAPPY=ON  \
      -DARROW_WITH_BROTLI=ON  \
      -DARROW_PARQUET=ON  \
      -DARROW_PYTHON=ON \
      -DARROW_PLASMA=ON \
      -DARROW_CUDA=ON \
      -DARROW_BUILD_TESTS=ON  \
      -DARROW_BUILD_EXAMPLES=ON \
      -DARROW_BUILD_BENCHMARKS=ON \
      -DARROW_BUILD_BENCHMARKS_REFERENCE=ON \
      -DARROW_BUILD_UTILITIES=ON \
      -DPARQUET_BUILD_EXECUTABLES=ON \
      -DPARQUET_BUILD_EXAMPLES=ON \
      -DPYTHON_EXECUTABLE=/usr/bin/python3

Did not find release/_cuda.cpython-36m-x86_64-linux-gnu.so
Cython module _cuda failure permitted
Did not find release/_flight.cpython-36m-x86_64-linux-gnu.so
Cython module _flight failure permitted
Did not find release/_parquet.cpython-36m-x86_64-linux-gnu.so
Cython module _parquet failure permitted
Did not find release/_orc.cpython-36m-x86_64-linux-gnu.so
Cython module _orc failure permitted
Did not find release/_plasma.cpython-36m-x86_64-linux-gnu.so
Cython module _plasma failure permitted
Did not find release/gandiva.cpython-36m-x86_64-linux-gnu.so
Cython module gandiva failure permitted

--------------------------------------------------------------------------------

ngd@node1:~/Sources/arrow$ sudo pip3 install pyarrow
WARNING: The directory '/home/ngd/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you may want sudo's -H flag.
Collecting pyarrow
  Downloading pyarrow-0.16.0.tar.gz (5.7 MB)
     |████████████████████████████████| 5.7 MB 2.5 MB/s 
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
    Preparing wheel metadata ... done
Requirement already satisfied: numpy>=1.14 in /usr/local/lib/python3.5/dist-packages (from pyarrow) (1.18.1)
Requirement already satisfied: six>=1.0.0 in /usr/lib/python3/dist-packages (from pyarrow) (1.10.0)
Building wheels for collected packages: pyarrow
  Building wheel for pyarrow (PEP 517) ... error
  ERROR: Command errored out with exit status 1:
   command: /usr/bin/python3 /usr/local/lib/python3.5/dist-packages/pip/_vendor/pep517/_in_process.py build_wheel /tmp/tmp4tfd98mc
       cwd: /tmp/pip-install-exm6pasn/pyarrow
  Complete output (508 lines):
  running bdist_wheel
  running build
  running build_py
  creating build
  creating build/lib.linux-aarch64-3.5
  creating build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/ipc.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/util.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/serialization.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/pandas_compat.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/filesystem.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/plasma.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/jvm.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/compute.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/cuda.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/fs.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/feather.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/csv.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/orc.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/json.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_generated_version.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/types.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/__init__.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/flight.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/dataset.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/compat.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/parquet.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/benchmark.py -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/hdfs.py -> build/lib.linux-aarch64-3.5/pyarrow
  creating build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_strategies.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_cuda_numba_interop.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/util.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_extension_type.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_sparse_tensor.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_types.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_flight.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_array.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_parquet.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_memory.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_cuda.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/strategies.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_dataset.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_plasma_tf_op.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_io.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_jvm.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_filesystem.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/deserialize_buffer.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_compute.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_tensor.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_serialization.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_orc.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_fs.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_json.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_table.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_gandiva.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_pandas.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_deprecations.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_ipc.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_builder.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/pandas_examples.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_cython.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/conftest.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_scalars.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_convert_builtin.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_schema.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/__init__.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_plasma.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_misc.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_hdfs.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_csv.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  copying pyarrow/tests/test_feather.py -> build/lib.linux-aarch64-3.5/pyarrow/tests
  running egg_info
  writing pyarrow.egg-info/PKG-INFO
  writing requirements to pyarrow.egg-info/requires.txt
  writing top-level names to pyarrow.egg-info/top_level.txt
  writing entry points to pyarrow.egg-info/entry_points.txt
  writing dependency_links to pyarrow.egg-info/dependency_links.txt
  warning: Failed to find the configured license file '../LICENSE.txt'
  reading manifest file 'pyarrow.egg-info/SOURCES.txt'
  reading manifest template 'MANIFEST.in'
  warning: no files found matching '../LICENSE.txt'
  warning: no files found matching '../NOTICE.txt'
  warning: no previously-included files matching '*.so' found anywhere in distribution
  warning: no previously-included files matching '*.pyc' found anywhere in distribution
  warning: no previously-included files matching '*~' found anywhere in distribution
  warning: no previously-included files matching '#*' found anywhere in distribution
  warning: no previously-included files matching '.git*' found anywhere in distribution
  warning: no previously-included files matching '.DS_Store' found anywhere in distribution
  no previously-included directories found matching '.asv'
  writing manifest file 'pyarrow.egg-info/SOURCES.txt'
  copying pyarrow/__init__.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_compute.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_compute.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_csv.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_csv.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_cuda.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_cuda.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_dataset.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_dataset.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_flight.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_flight.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_fs.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_fs.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_fs.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_hdfs.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_hdfs.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_json.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_json.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_orc.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_orc.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_parquet.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_parquet.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_parquet.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_plasma.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_s3fs.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/_s3fs.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/array.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/benchmark.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/builder.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/compute.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/error.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/feather.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/gandiva.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/io-hdfs.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/io.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/ipc.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/lib.cpp -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/lib.pxd -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/lib.pyx -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/lib_api.h -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/memory.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/pandas-shim.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/plasma-store-server -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/public-api.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/scalar.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/serialization.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/table.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/tensor.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  copying pyarrow/types.pxi -> build/lib.linux-aarch64-3.5/pyarrow
  creating build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache
  copying pyarrow/.pytest_cache/CACHEDIR.TAG -> build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache
  copying pyarrow/.pytest_cache/README.md -> build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache
  creating build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache/v
  creating build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache/v/cache
  copying pyarrow/.pytest_cache/v/cache/nodeids -> build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache/v/cache
  copying pyarrow/.pytest_cache/v/cache/stepwise -> build/lib.linux-aarch64-3.5/pyarrow/.pytest_cache/v/cache
  creating build/lib.linux-aarch64-3.5/pyarrow/include
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/array.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/buffer.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/buffer_builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/compare.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/extension_type.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/memory_pool.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/memory_pool_test.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/pretty_print.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/record_batch.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/result.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/scalar.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/sparse_tensor.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/status.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/stl.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/table.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/table_builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/tensor.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/type.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/type_fwd.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/type_traits.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/visitor.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  copying pyarrow/include/arrow/visitor_inline.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_adaptive.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_base.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_binary.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_decimal.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_dict.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_nested.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_primitive.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_time.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/builder_union.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/concatenate.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/diff.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  copying pyarrow/include/arrow/array/validate.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/array
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/benchmark_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/context.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/expression.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/kernel.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/logical_type.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/operation.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/test_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  copying pyarrow/include/arrow/compute/type_fwd.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/add.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/aggregate.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/boolean.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/cast.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/compare.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/count.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/filter.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/hash.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/isin.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/mean.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/minmax.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/sort_to_indices.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/sum.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  copying pyarrow/include/arrow/compute/kernels/take.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/compute/kernels
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/chunker.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/column_builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/converter.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/options.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/parser.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/reader.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  copying pyarrow/include/arrow/csv/test_common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/csv
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/dataset.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/discovery.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/disk_store.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/file_base.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/file_ipc.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/file_parquet.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/filter.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/partition.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/projector.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/scanner.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/test_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/transaction.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/type_fwd.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/visibility.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  copying pyarrow/include/arrow/dataset/writer.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/dataset
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/filesystem.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/hdfs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/localfs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/mockfs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/path_forest.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/path_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/s3fs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  copying pyarrow/include/arrow/filesystem/test_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/filesystem
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/buffered.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/compressed.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/concurrency.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/file.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/hdfs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/interfaces.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/memory.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/mman.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/slow.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  copying pyarrow/include/arrow/io/test_common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/io
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/dictionary.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/feather.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/json_integration.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/json_simple.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/message.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/options.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/reader.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/test_common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  copying pyarrow/include/arrow/ipc/writer.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/ipc
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/chunked_builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/chunker.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/converter.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/options.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/parser.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/rapidjson_defs.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/reader.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  copying pyarrow/include/arrow/json/test_common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/json
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/arrow_to_pandas.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/benchmark.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/config.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/datetime.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/decimal.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/deserialize.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/extension_type.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/flight.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/helpers.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/inference.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/init.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/io.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/iterators.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/numpy_convert.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/numpy_interop.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/numpy_to_arrow.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/platform.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/pyarrow.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/pyarrow_api.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/pyarrow_lib.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/python_to_arrow.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/serialize.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/type_traits.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  copying pyarrow/include/arrow/python/visibility.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/python
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/extension_type.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/generator.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/gtest_common.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/gtest_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/random.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  copying pyarrow/include/arrow/testing/util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/testing
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/align_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/atomic_shared_ptr.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/base64.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/basic_decimal.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/bit_stream_utils.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/bit_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/bpacking.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/checked_cast.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compare.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compiler_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_brotli.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_bz2.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_lz4.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_snappy.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_zlib.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/compression_zstd.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/config.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/cpu_info.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/decimal.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/delimiting.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/double_conversion.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/formatting.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/functional.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/hash_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/hashing.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/int_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/io_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/iterator.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/key_value_metadata.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/logging.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/macros.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/make_unique.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/memory.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/neon_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/optional.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/parallel.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/parsing.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/print.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/range.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/rle_encoding.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/sort.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/sse_util.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/stopwatch.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/string.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/string_builder.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/string_view.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/task_group.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/thread_pool.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/time.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/trie.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/type_traits.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/ubsan.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/uri.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/utf8.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/variant.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/vector.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/visibility.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  copying pyarrow/include/arrow/util/windows_compatibility.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/util
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  copying pyarrow/include/arrow/vendored/datetime.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  copying pyarrow/include/arrow/vendored/optional.hpp -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  copying pyarrow/include/arrow/vendored/string_view.hpp -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  copying pyarrow/include/arrow/vendored/variant.hpp -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  copying pyarrow/include/arrow/vendored/xxhash.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  copying pyarrow/include/arrow/vendored/datetime/date.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  copying pyarrow/include/arrow/vendored/datetime/ios.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  copying pyarrow/include/arrow/vendored/datetime/tz.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  copying pyarrow/include/arrow/vendored/datetime/tz_private.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  copying pyarrow/include/arrow/vendored/datetime/visibility.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/datetime
  creating build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/bignum-dtoa.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/bignum.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/cached-powers.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/diy-fp.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/double-conversion.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/fast-dtoa.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/fixed-dtoa.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/ieee.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/strtod.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  copying pyarrow/include/arrow/vendored/double-conversion/utils.h -> build/lib.linux-aarch64-3.5/pyarrow/include/arrow/vendored/double-conversion
  creating build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/__init__.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/common.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libarrow.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libarrow_cuda.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libarrow_dataset.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libarrow_flight.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libarrow_fs.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libgandiva.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  copying pyarrow/includes/libplasma.pxd -> build/lib.linux-aarch64-3.5/pyarrow/includes
  creating build/lib.linux-aarch64-3.5/pyarrow/tensorflow
  copying pyarrow/tensorflow/plasma_op.cc -> build/lib.linux-aarch64-3.5/pyarrow/tensorflow
  creating build/lib.linux-aarch64-3.5/pyarrow/tensorflow/plasma_op.so.dSYM
  creating build/lib.linux-aarch64-3.5/pyarrow/tensorflow/plasma_op.so.dSYM/Contents
  copying pyarrow/tensorflow/plasma_op.so.dSYM/Contents/Info.plist -> build/lib.linux-aarch64-3.5/pyarrow/tensorflow/plasma_op.so.dSYM/Contents
  copying pyarrow/tests/pyarrow_cython_example.pyx -> build/lib.linux-aarch64-3.5/pyarrow/tests
  creating build/lib.linux-aarch64-3.5/pyarrow/tests/data
  creating build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/README.md -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.emptyFile.jsn.gz -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.emptyFile.orc -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.test1.jsn.gz -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.test1.orc -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.testDate1900.jsn.gz -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/TestOrcFile.testDate1900.orc -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/decimal.jsn.gz -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  copying pyarrow/tests/data/orc/decimal.orc -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/orc
  creating build/lib.linux-aarch64-3.5/pyarrow/tests/data/parquet
  copying pyarrow/tests/data/parquet/v0.7.1.all-named-index.parquet -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/parquet
  copying pyarrow/tests/data/parquet/v0.7.1.column-metadata-handling.parquet -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/parquet
  copying pyarrow/tests/data/parquet/v0.7.1.parquet -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/parquet
  copying pyarrow/tests/data/parquet/v0.7.1.some-named-index.parquet -> build/lib.linux-aarch64-3.5/pyarrow/tests/data/parquet
  running build_ext
  creating /tmp/pip-install-exm6pasn/pyarrow/build/temp.linux-aarch64-3.5
  -- Running cmake for pyarrow
  cmake -DPYTHON_EXECUTABLE=/usr/bin/python3  -DPYARROW_BUILD_CUDA=off -DPYARROW_BUILD_FLIGHT=off -DPYARROW_BUILD_GANDIVA=off -DPYARROW_BUILD_DATASET=off -DPYARROW_BUILD_ORC=off -DPYARROW_BUILD_PARQUET=off -DPYARROW_BUILD_PLASMA=off -DPYARROW_BUILD_S3=off -DPYARROW_BUILD_HDFS=off -DPYARROW_USE_TENSORFLOW=off -DPYARROW_BUNDLE_ARROW_CPP=off -DPYARROW_BUNDLE_BOOST=off -DPYARROW_GENERATE_COVERAGE=off -DPYARROW_BOOST_USE_SHARED=on -DPYARROW_PARQUET_USE_SHARED=on -DCMAKE_BUILD_TYPE=release /tmp/pip-install-exm6pasn/pyarrow
  -- The C compiler identification is GNU 6.5.0
  -- The CXX compiler identification is GNU 6.5.0
  -- Check for working C compiler: /usr/bin/cc
  -- Check for working C compiler: /usr/bin/cc -- works
  -- Detecting C compiler ABI info
  -- Detecting C compiler ABI info - done
  -- Detecting C compile features
  -- Detecting C compile features - done
  -- Check for working CXX compiler: /usr/bin/c++
  -- Check for working CXX compiler: /usr/bin/c++ -- works
  -- Detecting CXX compiler ABI info
  -- Detecting CXX compiler ABI info - done
  -- Detecting CXX compile features
  -- Detecting CXX compile features - done
  -- Performing Test CXX_SUPPORTS_SSE4_2
  -- Performing Test CXX_SUPPORTS_SSE4_2 - Failed
  -- Performing Test CXX_SUPPORTS_ALTIVEC
  -- Performing Test CXX_SUPPORTS_ALTIVEC - Failed
  -- Performing Test CXX_SUPPORTS_ARMCRC
  -- Performing Test CXX_SUPPORTS_ARMCRC - Success
  -- Performing Test CXX_SUPPORTS_ARMV8_CRC_CRYPTO
  -- Performing Test CXX_SUPPORTS_ARMV8_CRC_CRYPTO - Success
  -- Arrow build warning level: PRODUCTION
  Using ld linker
  Configured for RELEASE build (set with cmake -DCMAKE_BUILD_TYPE={release,debug,...})
  -- Build Type: RELEASE
  -- Build output directory: /tmp/pip-install-exm6pasn/pyarrow/build/temp.linux-aarch64-3.5/release
  -- Found PythonInterp: /usr/bin/python3 (found version "3.5.2")
  -- Searching for Python libs in /usr/lib64;/usr/lib;/usr/lib/python3.5/config-3.5m-aarch64-linux-gnu
  -- Looking for python3.5m
  -- Found Python lib /usr/lib/python3.5/config-3.5m-aarch64-linux-gnu/libpython3.5m.so
  -- Found PythonLibs: /usr/lib/python3.5/config-3.5m-aarch64-linux-gnu/libpython3.5m.so
  -- Found NumPy: version "1.18.1" /usr/local/lib/python3.5/dist-packages/numpy/core/include
  -- Searching for Python libs in /usr/lib64;/usr/lib;/usr/lib/python3.5/config-3.5m-aarch64-linux-gnu
  -- Looking for python3.5m
  -- Found Python lib /usr/lib/python3.5/config-3.5m-aarch64-linux-gnu/libpython3.5m.so
  -- Could NOT find PkgConfig (missing:  PKG_CONFIG_EXECUTABLE)
  -- Found Arrow: /usr/include (found version "0.16.0")
  -- Arrow version: 0.16.0 (CMake package configuration: Arrow)
  -- Arrow SO and ABI version: 16
  -- Arrow full SO version: 16.0.0
  -- Found the Arrow core shared library: /usr/lib/aarch64-linux-gnu/libarrow.so
  -- Found the Arrow core import library:
  -- Found the Arrow core static library: /usr/lib/aarch64-linux-gnu/libarrow.a
  CMake Warning at cmake_modules/FindArrow.cmake:206 (find_package):
    Could not find a package configuration file provided by "ArrowPython" with
    any of the following names:
  
      ArrowPythonConfig.cmake
      arrowpython-config.cmake
  
    Add the installation prefix of "ArrowPython" to CMAKE_PREFIX_PATH or set
    "ArrowPython_DIR" to a directory containing one of the above files.  If
    "ArrowPython" provides a separate development package or SDK, be sure it
    has been installed.
  Call Stack (most recent call first):
    cmake_modules/FindArrow.cmake:313 (arrow_find_package_cmake_package_configuration)
    cmake_modules/FindArrowPython.cmake:49 (arrow_find_package)
    CMakeLists.txt:204 (find_package)
  
  
  CMake Error at /usr/share/cmake-3.5/Modules/FindPackageHandleStandardArgs.cmake:148 (message):
    Could NOT find ArrowPython (missing: ARROW_PYTHON_INCLUDE_DIR
    ARROW_PYTHON_LIB_DIR) (found version "0.16.0")
  Call Stack (most recent call first):
    /usr/share/cmake-3.5/Modules/FindPackageHandleStandardArgs.cmake:388 (_FPHSA_FAILURE_MESSAGE)
    cmake_modules/FindArrowPython.cmake:76 (find_package_handle_standard_args)
    CMakeLists.txt:204 (find_package)
  
  
  -- Configuring incomplete, errors occurred!
  See also "/tmp/pip-install-exm6pasn/pyarrow/build/temp.linux-aarch64-3.5/CMakeFiles/CMakeOutput.log".
  See also "/tmp/pip-install-exm6pasn/pyarrow/build/temp.linux-aarch64-3.5/CMakeFiles/CMakeError.log".
  error: command 'cmake' failed with exit status 1
  ----------------------------------------
  ERROR: Failed building wheel for pyarrow
Failed to build pyarrow
ERROR: Could not build wheels for pyarrow which use PEP 517 and cannot be installed directly
ngd@node1:~/Sources/arrow$ 


