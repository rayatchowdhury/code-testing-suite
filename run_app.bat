@echo off
REM Batch script to run the Python application with gRPC suppression

REM Set environment variables to suppress gRPC noise
set GRPC_VERBOSITY=NONE
set GRPC_TRACE=
set TF_CPP_MIN_LOG_LEVEL=3
set GLOG_minloglevel=3
set GRPC_ENABLE_FORK_SUPPORT=0
set GRPC_POLL_STRATEGY=poll

REM Suppress Python warnings
set PYTHONWARNINGS=ignore

REM Run the Python application
python main.py

REM Pause to see any output (optional)
REM pause
