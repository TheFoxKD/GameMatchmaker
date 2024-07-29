from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from uuid import UUID, uuid4
import heapq
from collections import Counter
import random


@dataclass(order=True)
class Player:
    priority_score: float = field(init=False)
    waiting_time: int
    mmr: int
    user_id: UUID = field(compare=False)
    roles: List[str] = field(compare=False)

    def __post_init__(self):
        self.priority_score = self._calculate_priority_score()

    def _calculate_priority_score(self, waiting_time_weight=0.7, mmr_weight=0.3):
        normalized_waiting_time = self.waiting_time / 1000  # Assuming max waiting time is 1000
        normalized_mmr = self.mmr / 3000  # Assuming max MMR is 3000
        return -(waiting_time_weight * normalized_waiting_time + mmr_weight * normalized_mmr)


@dataclass
class Team:
    side: str
    players: List[Tuple[Player, str]]

    @property
    def total_mmr(self):
        return sum(player.mmr for player, _ in self.players)


@dataclass
class Match:
    match_id: UUID
    teams: List[Team]

    @property
    def mmr_difference(self):
        return abs(self.teams[0].total_mmr - self.teams[1].total_mmr)


class MatchmakingService:
    def __init__(self):
        self.player_pool = []

    def add_players(self, players: List[Dict]):
        for player in players:
            heapq.heappush(
                self.player_pool,
                Player(
                    waiting_time=player['waitingTime'],
                    mmr=player['mmr'],
                    user_id=UUID(player['user_id']),
                    roles=player['roles']
                )
            )

    def create_matches(self, team_size: int = 5) -> List[Match]:
        matches = []
        while len(self.player_pool) >= team_size * 2:
            match = self._create_single_match(team_size)
            if match:
                matches.append(match)
            else:
                break
        return matches

    def _create_single_match(self, team_size: int) -> Match:
        players = [heapq.heappop(self.player_pool) for _ in range(team_size * 2)]

        team_red, team_blue = self._distribute_players(players)
        team_red = self._assign_roles(team_red)
        team_blue = self._assign_roles(team_blue)

        match = Match(
            match_id=uuid4(),
            teams=[
                Team("red", team_red),
                Team("blue", team_blue)
            ]
        )

        self._balance_teams(match)

        return match

    def _distribute_players(self, players: List[Player]) -> Tuple[List[Player], List[Player]]:
        players.sort(key=lambda p: p.mmr, reverse=True)
        team_red, team_blue = [], []
        for i, player in enumerate(players):
            if i % 2 == 0:
                team_red.append(player)
            else:
                team_blue.append(player)
        return team_red, team_blue

    def _assign_roles(self, team: List[Player]) -> List[Tuple[Player, str]]:
        roles = ["top", "jungle", "mid", "bot", "sup"]
        assignments = []

        for role in roles:
            best_player = max(team, key=lambda p: p.roles.index(role))
            assignments.append((best_player, role))
            team.remove(best_player)

        return assignments

    def _balance_teams(self, match: Match):
        max_iterations = 100
        best_difference = match.mmr_difference
        best_teams = match.teams.copy()

        for _ in range(max_iterations):
            team1, team2 = match.teams
            for i in range(len(team1.players)):
                for j in range(len(team2.players)):
                    if team1.players[i][1] == team2.players[j][1]:  # Same role
                        # Swap players
                        team1.players[i], team2.players[j] = team2.players[j], team1.players[i]

                        new_difference = abs(team1.total_mmr - team2.total_mmr)
                        if new_difference < best_difference:
                            best_difference = new_difference
                            best_teams = [Team(team1.side, team1.players.copy()),
                                          Team(team2.side, team2.players.copy())]

                        # Swap back for next iteration
                        team1.players[i], team2.players[j] = team2.players[j], team1.players[i]

        match.teams = best_teams


def process_matchmaking(players: List[Dict]) -> List[Dict]:
    service = MatchmakingService()
    service.add_players(players)
    matches = service.create_matches()

    return [
        {
            "match_id": str(match.match_id),
            "teams": [
                {
                    "side": team.side,
                    "users": [{"id": str(player.user_id), "role": role} for player, role in team.players]
                }
                for team in match.teams
            ]
        }
        for match in matches
    ]


# Example usage and basic test
if __name__ == "__main__":
    import random


    def generate_test_players(num_players):
        return [
            {
                "user_id": str(uuid4()),
                "mmr": random.randint(1000, 3000),
                "roles": random.sample(["top", "jungle", "mid", "bot", "sup"], k=5),
                "waitingTime": random.randint(1, 1000)
            }
            for _ in range(num_players)
        ]


    test_players = generate_test_players(100)
    result = process_matchmaking(test_players)

    print(f"Number of matches created: {len(result)}")
    for match in result:
        print(f"Match ID: {match['match_id']}")
        for team in match['teams']:
            print(f"  {team['side']} team:")
            team_mmr = 0
            for player in team['users']:
                player_data = next(p for p in test_players if p['user_id'] == player['id'])
                team_mmr += player_data['mmr']
                print(f"    Player ID: {player['id']}, Role: {player['role']}, MMR: {player_data['mmr']}")
            print(f"  Team Total MMR: {team_mmr}")
        print()

    # Basic assertions
    assert len(result) > 0, "Expected at least one match to be created"
    assert all(len(match['teams']) == 2 for match in result), "Each match should have 2 teams"
    assert all(
        len(team['users']) == 5 for match in result for team in match['teams']
    ), "Each team should have 5 players"
    assert all(
        player['role'] in ["top", "jungle", "mid", "bot", "sup"]
        for match in result
        for team in match['teams']
        for player in team['users']
    ), "All roles should be valid"

    # Check MMR balance
    for match in result:
        team_mmrs = [sum(next(p for p in test_players if p['user_id'] == player['id'])['mmr']
                         for player in team['users'])
                     for team in match['teams']]
        mmr_difference = abs(team_mmrs[0] - team_mmrs[1])
        assert mmr_difference <= 500, f"MMR difference too high: {mmr_difference}"

    print("All tests passed!")