#!/usr/bin/env python3
"""
GitHub Activity CLI - Fetch and display recent GitHub user activity
"""

import argparse
import sys
import requests
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box


class GitHubActivity:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GitHub-Activity-CLI/1.0',
            'Accept': 'application/vnd.github.v3+json'
        })

    def fetch_user_activity(self, username):
        """Fetch recent activity for a GitHub user"""
        url = f"{self.base_url}/users/{username}/events"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                self.console.print(
                    f"[red]Error: User '{username}' not found[/red]")
            else:
                self.console.print(f"[red]Error: {e}[/red]")
            return None
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Network error: {e}[/red]")
            return None

    def parse_event(self, event):
        """Parse GitHub event data into a readable format"""
        event_type = event.get('type', '')
        repo_name = event.get('repo', {}).get('name', 'N/A')
        created_at = event.get('created_at', '')

        # Format timestamp
        if created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = 'N/A'

        # Parse payload based on event type
        payload = event.get('payload', {})
        description = self._get_event_description(event_type, payload, repo_name)

        return {
            'timestamp': timestamp,
            'description': description
        }

    def _get_event_description(self, event_type, payload, repository):
        """Generate human-readable description for each event type"""
        descriptions = {
            'PushEvent': f"Pushed {payload.get('size', 0) } commits to { repository }",
            'CreateEvent': f"Created { payload.get('ref_type', 'resource') } in { repository }",
            'DeleteEvent': f"Deleted {payload.get('ref_type', 'resource')} in { repository }",
            'PullRequestEvent': f"Pull request { payload.get('action', 'action') } in { repository }",
            'IssuesEvent': f"Issue {payload.get('action', 'action')} in { repository }",
            'IssueCommentEvent': f"Commented on issue in { repository }",
            'PullRequestReviewEvent': f"Reviewed a pull request in { repository }",
            'PullRequestReviewCommentEvent': 'Responded on a comment from a pull request in { repository }',
            'WatchEvent': f"Starred { repository }",
            'ForkEvent': f"Forked { repository }",
            'ReleaseEvent': f"Released {payload.get('release', {}).get('tag_name', '')}",
            'MemberEvent': f"Added member to { repository }"
        }

        return descriptions.get(event_type, f"Unknown event: {event_type}")

    def display_activity(self, username, events):
        """Display activity in a formatted table"""
        # Create table
        table = Table(
            title=f"Recent GitHub Activity for [bold green]{username}[/bold green]",
            box=box.ROUNDED,
            header_style="bold magenta",
            title_style="bold blue"
        )

        # Add columns
        table.add_column("Timestamp", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        # Add rows
        for event in events:
            parsed = self.parse_event(event)
            table.add_row(
                parsed['timestamp'],
                parsed['description']
            )

        # Display table
        self.console.print(table)

    def run(self):
        """Main CLI execution"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('username')
        args = parser.parse_args()

        if args.username:
            self.console.print(
                f"[blue]Fetching activity for {args.username}...[/blue]")
        events = self.fetch_user_activity(args.username)

        if events:
            self.display_activity(args.username, events)
        else:
            self.console.print(
                f"[yellow] {args.username} has no recent activity...[/yellow]")


def main():
    """Entry point for the CLI"""
    try:
        cli = GitHubActivity()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


main()
