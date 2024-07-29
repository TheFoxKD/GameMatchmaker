import random
import time
import unittest
from uuid import uuid4

from matchmaking_algorithm import process_matchmaking


class TestMatchmakingAlgorithm(unittest.TestCase):

    def generate_players(self, num_players, mmr_range=(1000, 3000)):
        return [
            {
                "user_id": str(uuid4()),
                "mmr": random.randint(*mmr_range),
                "roles": random.sample(["top", "jungle", "mid", "bot", "sup"], k=5),
                "waitingTime": random.randint(1, 1000)
            }
            for _ in range(num_players)
        ]

    def test_large_number_of_players(self):
        players = self.generate_players(10 ** 5)
        result = process_matchmaking(players)
        self.assertGreater(len(result), 0, "Should create at least one match")
        self.assertEqual(len(result) * 10, len([p for m in result for t in m['teams'] for p in t['users']]),
                         "All matches should have 10 players")

    def test_role_distribution(self):
        players = self.generate_players(10)
        for player in players:
            player['roles'] = ['mid', 'top', 'jungle', 'bot', 'sup']  # Set preferred role to 'mid'
        result = process_matchmaking(players)
        mid_players = [p for m in result for t in m['teams'] for p in t['users'] if p['role'] == 'mid']
        self.assertEqual(len(mid_players), 2, "Each match should have 2 mid players")

    def test_mmr_balance(self):
        players = [
            {"user_id": str(uuid4()), "mmr": 2000, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2100, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2200, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2300, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2400, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2500, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2600, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2700, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2800, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
            {"user_id": str(uuid4()), "mmr": 2900, "roles": ["top", "mid", "bot", "sup", "jungle"], "waitingTime": 10},
        ]
        result = process_matchmaking(players)
        self.assertEqual(len(result), 1, "Should create exactly one match")
        team_mmrs = [
            sum(next(p for p in players if p['user_id'] == user['id'])['mmr'] for user in team['users'])
            for team in result[0]['teams']
        ]
        self.assertLess(abs(team_mmrs[0] - team_mmrs[1]), 1000, "Teams should have reasonably similar total MMR")
        print(f"MMR difference: {abs(team_mmrs[0] - team_mmrs[1])}")

    def test_insufficient_players(self):
        players = self.generate_players(9)  # Not enough for a full match
        result = process_matchmaking(players)
        self.assertEqual(len(result), 0, "Should not create any matches with insufficient players")

    def test_performance(self):
        players = self.generate_players(10 ** 5)
        start_time = time.time()
        process_matchmaking(players)
        end_time = time.time()
        execution_time = end_time - start_time
        self.assertLess(execution_time, 60*10,
                        f"Matchmaking should complete in less than 10 seconds, took {execution_time:.2f} seconds")


if __name__ == '__main__':
    unittest.main()
