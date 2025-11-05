#!/usr/bin/env python3
"""
US Chess Rating Tracker
Fetches and displays tournament sections with real-time rating changes
"""

import requests
import json
import argparse
from datetime import datetime
from tabulate import tabulate


def fetch_member_sections(member_id, offset=0, size=50):
    """Fetch tournament sections for a US Chess member"""
    url = f"https://ratings-api.uschess.org/api/v1/members/{member_id}/sections"
    params = {
        "Offset": offset,
        "Size": size
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def format_date(date_string):
    """Format ISO date string to readable format"""
    if not date_string:
        return "N/A"
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime("%Y-%m-%d")
    except:
        return date_string


def calculate_rating_change(rating_before, rating_after):
    """Calculate and format rating change"""
    if rating_after is None or rating_before is None:
        return "Pending"

    change = rating_after - rating_before
    if change > 0:
        return f"+{change}"
    elif change < 0:
        return str(change)
    else:
        return "0"


def display_sections(data):
    """Display tournament sections in a formatted table"""
    if not data or 'items' not in data:
        print("No data available")
        return

    sections = data['items']

    if not sections:
        print("No tournament sections found")
        return

    # Display statistics
    print("\n" + "="*80)
    print("US CHESS RATING TRACKER")
    print("="*80)

    if sections:
        # Get the most recent rating
        latest = sections[0]
        rating_records = latest.get('ratingRecords', [])
        if rating_records:
            current_rating = rating_records[0].get('postRating') or rating_records[0].get('preRating') or 'N/A'
        else:
            current_rating = 'N/A'

        total_sections = len(sections)

        # Calculate total games and results (if available in the data)
        # Note: The API structure shown doesn't include games_played and score at the top level
        # We'll display what we have
        print(f"\nCurrent Rating: {current_rating}")
        print(f"Total Sections: {total_sections}")

    # Prepare table data
    table_data = []
    headers = [
        "Date",
        "Tournament",
        "Section",
        "Type",
        "Before",
        "After",
        "Change"
    ]

    for section in sections:
        # Get rating records
        rating_records = section.get('ratingRecords', [])
        rating_before = None
        rating_after = None
        rating_type = section.get('ratingSystem', 'R')

        if rating_records:
            rating_before = rating_records[0].get('preRating')
            rating_after = rating_records[0].get('postRating')

        change = calculate_rating_change(rating_before, rating_after)

        # Get event information
        event = section.get('event', {})
        event_name = event.get('name', 'N/A')
        event_date = event.get('endDate') or event.get('startDate', '')

        row = [
            format_date(event_date),
            event_name[:30],  # Truncate long names
            section.get('sectionName', 'N/A')[:20],
            rating_type,
            rating_before if rating_before is not None else 'N/A',
            rating_after if rating_after is not None else 'Pending',
            change
        ]
        table_data.append(row)

    # Display table
    print("\n" + "="*80)
    print("TOURNAMENT SECTIONS (Most Recent First)")
    print("="*80 + "\n")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="US Chess Rating Tracker - Fetches and displays tournament sections with real-time rating changes"
    )
    parser.add_argument(
        "-m", "--member-id",
        type=str,
        default="17323973",
        help="US Chess Member ID (default: 17323973)"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=50,
        help="Number of sections to fetch (default: 50)"
    )

    args = parser.parse_args()

    print("US Chess Rating Tracker")
    print("-" * 40)
    print(f"\nFetching data for member {args.member_id}...")

    # Fetch and display data
    data = fetch_member_sections(args.member_id, size=args.size)

    if data:
        display_sections(data)
    else:
        print("Failed to fetch data. Please check your internet connection and member ID.")


if __name__ == "__main__":
    main()
