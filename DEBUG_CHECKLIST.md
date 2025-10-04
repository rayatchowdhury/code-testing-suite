# Validator Debug Output - Quick Check

## What to do:

1. **Open a NEW terminal** (to see clean output)
2. Run: `py -m src.app`
3. Open **Validator window**
4. Click **"Run Tests"** or **"Start"**
5. **Immediately check the terminal**

## What you should see:

```
================================================================================
DEBUG: ValidatorTestWorker initialized
DEBUG: Workspace dir: C:\Users\Rayat\Desktop\code-testing-suite\workspace
DEBUG: Test count: 10
DEBUG: Executables: {'generator': '...', 'test': '...', 'validator': '...'}
DEBUG: Execution commands: {'generator': ['python', 'generator.py'], 'test': ['./test.exe'], 'validator': ['./validator.exe']}
================================================================================

DEBUG: run_tests() called - starting 10 tests
DEBUG: Max workers: 7

DEBUG: _run_single_test(1) started
DEBUG: Test 1 - Stage 1: Running generator
DEBUG: Generator command: ['python', 'generator.py']
...
```

## If you see NOTHING:

This means the worker isn't even being created or run_tests() isn't being called!

Possible causes:
1. Compilation failed (check for compilation errors in UI)
2. Files not saved/selected properly
3. Worker thread not starting

## If you see the init but NOT run_tests():

The worker was created but run_tests() was never called - UI issue or signal not connected.

## If you see run_tests() but NOT _run_single_test():

The thread pool isn't submitting jobs - possible crash on job submission.

---

**Just run it and tell me what you see (or don't see) in the terminal!**
