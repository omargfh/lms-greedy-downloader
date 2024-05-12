from console import info, error, success, warning, cprint

class TestKit:
    def __init__(self) -> None:
        self.tests = 0
        self.all_tests = []

        self.failed = 0
        self.optionalFailed = 0
        self.passed = 0
        self.optionalPassed = 0

    def done(self):
        stats = f"Tests: {self.tests}, Passed: {self.passed}, Failed: {self.failed}, Optional Passed: {self.optionalPassed}, Optional Failed: {self.optionalFailed}"
        if self.tests == self.optionalFailed + self.passed + self.optionalPassed:
            cprint(" " + stats, "success")
            success("All tests passed")
        else:
            cprint(stats, "error")
            error("Some tests failed")
            exit(0)

def it(name: str, acc: TestKit = None, optional: bool = False, help: str = None):
    acc = acc or TestKit()
    acc.tests += 1
    def decorator(fn):
        def wrapper(*args, **kwargs):
            info(f"Starting test {name}{optional and ' (optional)' or ''}")
            try:
                fn(*args, **kwargs)
                if optional:
                    acc.optionalPassed += 1
                else:
                    acc.passed += 1
                success(f"✅ {name}")
            except Exception as e:
                if optional:
                    acc.optionalFailed += 1
                else:
                    acc.failed += 1
                error(f"❌ {name}")
                error(e.__str__().strip())
                if help:
                    warning(help)
        return wrapper
    return decorator
