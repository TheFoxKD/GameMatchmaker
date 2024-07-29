# Matchmaking Algorithm

This project implements a matchmaking algorithm for a game where two teams of five players each compete against each other. The algorithm takes into account player MMR (Matchmaking Rating), preferred roles, and waiting time to create balanced and fair matches.

## Features

- Balances teams based on player MMR
- Assigns players to their preferred roles when possible
- Considers waiting time to prioritize players who have been in the queue longer
- Handles large numbers of players efficiently
- Creates multiple matches simultaneously when possible

## How it works

1. The algorithm receives a list of players with their MMR, preferred roles, and waiting time.
2. It sorts players into a priority queue based on a combination of their waiting time and MMR.
3. For each match, it selects the top 10 players from the queue.
4. It distributes these players into two teams, trying to balance the total MMR of each team.
5. Within each team, it assigns players to roles based on their preferences.
6. If necessary, it performs additional swaps between teams to further balance MMR while maintaining role assignments.

## Files

- `matchmaking_algorithm.py`: Contains the main logic for the matchmaking algorithm.
- `test_matchmaking.py`: Includes unit tests to verify the algorithm's functionality and performance.

## Usage

To use the matchmaking algorithm, import the `process_matchmaking` function from `matchmaking_algorithm.py`:

```python
from matchmaking_algorithm import process_matchmaking

players = [
    {
        "user_id": "4877bf28-68a8-4f6c-84a8-707223e9237b",
        "mmr": 2000,
        "roles": ["top", "mid", "bot", "sup", "jungle"],
        "waitingTime": 12
    },
    # ... more players ...
]

matches = process_matchmaking(players)
```

The `process_matchmaking` function returns a list of matches, where each match contains two teams with assigned players and roles.

## Testing

Run the unit tests using:

```
python -m unittest test_matchmaking.py
```

The tests cover various scenarios, including:
- Handling a large number of players
- Role distribution
- MMR balancing
- Performance with 100,000 players