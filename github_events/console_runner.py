import logging
import argparse
from . import GitHubEventProcessor


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('--key')
    parser.add_argument('--command')
    parser.add_argument('-d', '--no-delete', action='store_true', default=False)
    parser.add_argument('path')

    args = parser.parse_args()

    app = GitHubEventProcessor(args.path, args.key, args.command)

    app.parse_events()
    app.process_events()
    if not args.no_delete:
        app.clear_events()
    pass


if __name__ == '__main__':
    main()
