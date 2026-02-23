#!/usr/bin/env python3
"""Demo script for LocalDependencyManager.

This script demonstrates building bdwgc and pcre2 from the embedded
ext/ sources and caching them in platform-specific directories.

Usage:
    python -m shedskin.scripts.demo_local_deps [--force] [--status]

Options:
    --force     Force rebuild even if targets exist
    --status    Show status only, don't build
    --bdwgc     Build only bdwgc
    --pcre2     Build only pcre2
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for direct script execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shedskin.cmake import LocalDependencyManager


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build dependencies from embedded ext/ sources"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force rebuild even if targets exist"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show status only, don't build"
    )
    parser.add_argument("--bdwgc", action="store_true", help="Build only bdwgc")
    parser.add_argument("--pcre2", action="store_true", help="Build only pcre2")
    parser.add_argument(
        "--reset", action="store_true", help="Reset cache before building"
    )

    args = parser.parse_args()

    # Initialize the manager
    ldm = LocalDependencyManager(reset_on_run=args.reset)

    if args.status:
        # Just show status
        status = ldm.status()
        print("\nLocalDependencyManager Status:")
        print("-" * 40)
        for key, value in status.items():
            print(f"  {key}: {value}")
        print()
        return 0

    # Build specific or all dependencies
    try:
        if args.bdwgc:
            ldm.install_bdwgc(force=args.force)
        elif args.pcre2:
            ldm.install_pcre2(force=args.force)
        else:
            ldm.install_all(force=args.force)

        # Show final status
        print("\n" + "=" * 60)
        print("Build Complete!")
        print("=" * 60)
        status = ldm.status()
        print(f"  Include dir: {ldm.get_include_dir()}")
        print(f"  Library dir: {ldm.get_lib_dir()}")
        print(f"  bdwgc built: {status['bdwgc_built']}")
        print(f"  pcre2 built: {status['pcre2_built']}")
        print()

        return 0

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return 1
    except Exception as e:
        print(f"\nBuild failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
