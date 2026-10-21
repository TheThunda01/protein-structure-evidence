"""Keep link-specific checks explicit on hosts without symlink privileges."""
import errno
import os


def create_symlink_or_skip(testcase, link, target, *, target_is_directory=False):
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except OSError as exc:
        if os.environ.get("REQUIRE_SYMLINK_TESTS") == "1":
            raise
        unsupported = {errno.EPERM, errno.EACCES, errno.ENOSYS, errno.ENOTSUP}
        if getattr(exc, "winerror", None) == 1314 or exc.errno in unsupported:
            testcase.skipTest("This account or filesystem cannot create symbolic links")
        raise
