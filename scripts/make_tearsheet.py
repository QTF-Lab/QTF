"""
Command-line script to generate a tearsheet from a backtest artifact.
"""
from __future__ import annotations
import argparse


def main() -> None:
    """Main function to parse arguments and generate a tearsheet."""
    parser = argparse.ArgumentParser(description="Generate a tearsheet from backtest results.")
    parser.add_argument(
        "--results",
        required=True,
        type=str,
        help="Path to the backtest results artifact (e.g., a pickle file).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Path to save the output HTML tearsheet.",
    )
    args = parser.parse_args()

    print(f"Loading backtest results from: {args.results}")
    # In a real implementation, load the equity curve and trades data here.
    print(f"Generating tearsheet at: {args.output}")
    # create_html_tearsheet(...)
    print("Tearsheet generation complete.")


if __name__ == "__main__":
    main()
