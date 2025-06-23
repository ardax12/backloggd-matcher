import exporter
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "user1",
    type=str,
)

parser.add_argument(
    "user2",
    type=str,
)

args = parser.parse_args()

username1 = args.user1
username2 = args.user2

user1data = exporter.fetch_all_game_data(f"https://backloggd.com/u/{username1}/games/")
user2data = exporter.fetch_all_game_data(f"https://backloggd.com/u/{username2}/games/")