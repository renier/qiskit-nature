# This code is part of Qiskit.
#
# (C) Copyright IBM 2019, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Contains the version."""

import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
QISKIT_DIR = os.path.dirname(ROOT_DIR)


def _minimal_ext_cmd(cmd):
    # construct minimal environment
    env = {}
    for k in ["SYSTEMROOT", "PATH"]:
        v = os.environ.get(k)
        if v is not None:
            env[k] = v
    # LANGUAGE is used on win32
    env["LANGUAGE"] = "C"
    env["LANG"] = "C"
    env["LC_ALL"] = "C"
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=os.path.join(os.path.dirname(QISKIT_DIR)),
    ) as proc:
        stdout, stderr = proc.communicate()
        if proc.returncode > 0:
            raise OSError(
                "Command {} exited with code {}: {}".format(
                    cmd, proc.returncode, stderr.strip().decode("ascii")
                )
            )
        return stdout


def git_version():
    """Get the current git head sha1."""
    # Determine if we're at main
    try:
        out = _minimal_ext_cmd(["git", "rev-parse", "HEAD"])
        git_revision = out.strip().decode("ascii")
    except OSError:
        git_revision = "Unknown"

    return git_revision


with open(os.path.join(ROOT_DIR, "VERSION.txt"), "r", encoding="utf8") as version_file:
    VERSION = version_file.read().strip()


def get_version_info():
    """Get the full version string."""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of scipy.version messes
    # up the build under Python 3.
    full_version = VERSION

    if not os.path.exists(os.path.join(os.path.dirname(QISKIT_DIR), ".git")):
        return full_version
    try:
        release = _minimal_ext_cmd(["git", "tag", "-l", "--points-at", "HEAD"])
    except Exception:  # pylint: disable=broad-except
        return full_version
    git_revision = git_version()
    if not release:
        full_version += ".dev0+" + git_revision[:7]

    return full_version


__version__ = get_version_info()
