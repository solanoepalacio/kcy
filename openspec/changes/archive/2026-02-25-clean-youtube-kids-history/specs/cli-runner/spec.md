## ADDED Requirements

### Requirement: auth.py entry point
`auth.py` SHALL be a standalone runnable script that initiates the OAuth 2.0 device flow and saves the token. It SHALL take no required arguments.

#### Scenario: Running auth.py
- **WHEN** `python auth.py` is executed
- **THEN** the script starts the device flow, prints the verification URL and code, and saves `token.json` on success

### Requirement: clean_history.py entry point with --since flag
`clean_history.py` SHALL be a standalone runnable script accepting a required `--since` argument specifying the history window to scan (e.g., `1h`, `3h`, `12h`, `1d`).

#### Scenario: Running with a valid --since value
- **WHEN** `python clean_history.py --since 2h` is executed
- **THEN** the script scans the last 2 hours of watch history and removes any kids-targeted videos

#### Scenario: Running without --since
- **WHEN** `python clean_history.py` is executed without the `--since` argument
- **THEN** the script exits with an error message explaining that `--since` is required

#### Scenario: Running with an invalid --since value
- **WHEN** `python clean_history.py --since bad` is executed with an unrecognized duration format
- **THEN** the script exits with an error message showing the accepted format

### Requirement: clean_history.py --dry-run flag
`clean_history.py` SHALL support an optional `--dry-run` flag. When set, no deletions are made.

#### Scenario: Dry-run flag is passed
- **WHEN** `python clean_history.py --since 1h --dry-run` is executed
- **THEN** the script prints what would be removed without deleting anything

### Requirement: revoke.py entry point
`revoke.py` SHALL be a standalone runnable script that revokes the OAuth token server-side and deletes `token.json` locally.

#### Scenario: Running revoke.py with a valid token
- **WHEN** `python revoke.py` is executed and `token.json` exists
- **THEN** the script calls Google's revocation endpoint, deletes `token.json`, and prints a confirmation message

#### Scenario: Running revoke.py with no token file
- **WHEN** `python revoke.py` is executed and `token.json` does not exist
- **THEN** the script prints a message that no token was found and exits cleanly
