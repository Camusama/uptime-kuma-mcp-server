#!/usr/bin/env python3
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_version.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]
    if bump_type not in ["major", "minor", "patch"]:
        print("Invalid bump type. Use major/minor/patch")
        sys.exit(1)
    try:

        subprocess.run(f"bumpversion {bump_type}", shell=True, check=True)
        subprocess.run("git push", shell=True, check=True)
        subprocess.run("git push --tags", shell=True, check=True)

        print(f"Successfully bumped {bump_type} version and pushed to remote")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
