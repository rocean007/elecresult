"""
scraper/main.py — CLI entry point for the Nepal Election 2082 scraper.

Usage:
  python -m scraper.main                    # Full run: all 165 constituencies
  python -m scraper.main --async            # Use async scraper (faster)
  python -m scraper.main --constituency 45  # Single constituency
  python -m scraper.main --no-images        # Skip image downloads
  python -m scraper.main --watch 120        # Repeat every N seconds
"""

import argparse
import asyncio
import logging
import sys
import time

from scraper.utils import setup_logging
from scraper.scraper import ElectionScraper
from scraper.exporter import export_all
from scraper.image_downloader import run_downloads

logger = logging.getLogger(__name__)


def run_sync(args):
    scraper = ElectionScraper()
    logger.info("Starting synchronous full scrape…")

    if args.constituency:
        data = scraper.scrape_constituency(args.constituency)
        if data:
            from scraper.exporter import write_constituency_json
            write_constituency_json(data, args.constituency)
            logger.info(f"Saved constituency #{args.constituency}")
        else:
            logger.error("Scrape failed")
            sys.exit(1)
        return

    constituencies = scraper.scrape_constituency_list()
    if not constituencies:
        logger.error("Could not fetch constituency list — check network or site structure")
        sys.exit(1)

    logger.info(f"Fetching {len(constituencies)} constituency pages…")
    detailed = []
    for c in constituencies:
        detail = scraper.scrape_constituency(c["num"])
        if detail:
            detail.update({"district": c["district"], "province": c["province"]})
            detailed.append(detail)

    party_seats = scraper.scrape_party_seats()
    pr_data     = scraper.scrape_pr()
    export_all(detailed, party_seats, pr_data)

    if not args.no_images:
        party_ids = [p["id"] for p in party_seats.get("parties", [])]
        run_downloads(detailed, party_ids)


def run_async_scrape(args):
    from scraper.async_scraper import scrape_all_async
    from scraper.scraper import ElectionScraper

    logger.info("Starting async full scrape…")
    constituencies = asyncio.run(scrape_all_async())

    scraper = ElectionScraper()
    # Enrich with district/province from list page
    list_data = {c["num"]: c for c in scraper.scrape_constituency_list()}
    for c in constituencies:
        meta = list_data.get(c["num"], {})
        c.setdefault("district", meta.get("district", ""))
        c.setdefault("province", meta.get("province", ""))

    party_seats = scraper.scrape_party_seats()
    pr_data     = scraper.scrape_pr()
    export_all(constituencies, party_seats, pr_data)

    if not args.no_images:
        party_ids = [p["id"] for p in party_seats.get("parties", [])]
        run_downloads(constituencies, party_ids)


def main():
    parser = argparse.ArgumentParser(description="Nepal Election 2082 Scraper")
    parser.add_argument("--async",        dest="use_async",    action="store_true", help="Use async scraper (faster)")
    parser.add_argument("--constituency", type=int,            metavar="N",         help="Scrape only constituency N (1–165)")
    parser.add_argument("--no-images",    dest="no_images",    action="store_true", help="Skip image downloads")
    parser.add_argument("--watch",        type=int,            metavar="SECONDS",   help="Repeat every N seconds")
    parser.add_argument("--verbose",      action="store_true", help="Debug logging")
    args = parser.parse_args()

    setup_logging(logging.DEBUG if args.verbose else logging.INFO)

    def once():
        if args.use_async:
            run_async_scrape(args)
        else:
            run_sync(args)

    if args.watch:
        logger.info(f"Watch mode: running every {args.watch}s — Ctrl+C to stop")
        while True:
            try:
                once()
            except Exception as e:
                logger.error(f"Run error: {e}")
            logger.info(f"Sleeping {args.watch}s…")
            time.sleep(args.watch)
    else:
        once()


if __name__ == "__main__":
    main()
