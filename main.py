import sys
from argparse import ArgumentParser
from typing import List

from scenarios import recalculate_metrics, crawl_find

if __name__ == '__main__':
    parser = ArgumentParser(prog='Ficbook Crawler')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_a = subparsers.add_parser('crawl_directions', help='a help')
    parser_a.add_argument('-d', '--directions',
                          type=int,
                          nargs='+',
                          choices=[1, 2, 3, 4, 5],
                          help='bar help',
                          dest='directions',
                          default=[1, 2, 3, 4, 5])
    parser_a.add_argument('-r', '--page_range', type=int, nargs=2, help='Type two integers', dest='page_range', default=[1, 50])
    parser_a.add_argument('-c', '--count', type=int, help='Maximum count of novels per direction', dest='count', default=500)
    parser_b = subparsers.add_parser('recalculate_metrics')
    parser_b.add_argument('-go', action='store_true')

    args = parser.parse_args(sys.argv[1:])
    if args.go:
        recalculate_metrics()
    elif args.directions:
        crawl_find(directions=args.directions,
                   page_range=args.page_range,
                   max_count=args.count)
