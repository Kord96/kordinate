"""
klog CLI - test logging configuration.

Usage:
    klog test --app myapp
    klog test --app myapp --json
    klog test --app myapp --level debug
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="klog",
        description="klog - structured logging utility",
    )
    subparsers = parser.add_subparsers(dest="command")

    test_parser = subparsers.add_parser("test", help="Test logging configuration")
    test_parser.add_argument("--app", default="klog-test", help="Application name")
    test_parser.add_argument("--json", action="store_true", default=False, help="JSON output (default: console)")
    test_parser.add_argument("--level", default="debug", help="Log level (default: debug)")

    args = parser.parse_args()

    if args.command == "test":
        from klog import configure_logging, log

        configure_logging(
            app_name=args.app,
            level=args.level,
            json_output=args.json,
        )

        log.debug("debug message", logger="test", sample_key="sample_value")
        log.info("info message", logger="test", count=42)
        log.warning("warning message", logger="test", threshold=0.9)
        log.error("error message", logger="test", error_code="E001")

        with log.context(stage="context_test"):
            log.info("inside context", logger="test", nested=True)

        with log.trace_context(service=args.app) as trace_id:
            log.info("with trace", logger="test", trace_id=trace_id)

        print(f"\nklog test complete. App: {args.app}, Level: {args.level}", file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
