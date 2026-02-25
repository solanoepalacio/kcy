## ADDED Requirements

### Requirement: Device flow authentication
The `auth.py` script SHALL authenticate the user via the OAuth 2.0 Device Authorization Grant (RFC 8628) without requiring a browser on the host machine. It SHALL print the verification URL and user code to stdout, poll Google's token endpoint until the user approves, and save the resulting credentials to `token.json`.

#### Scenario: Successful first-time authentication
- **WHEN** `auth.py` is run and no `token.json` exists
- **THEN** the script prints a verification URL and a user code to stdout, polls for approval, and writes `token.json` upon successful authorization

#### Scenario: User approves on another device
- **WHEN** the user visits the verification URL on any device and enters the code
- **THEN** the script detects approval, saves `token.json`, and exits with a success message

#### Scenario: Token already exists
- **WHEN** `auth.py` is run and a valid `token.json` already exists
- **THEN** the script informs the user that a token is already present and exits without starting a new flow

### Requirement: Token caching and auto-refresh
Credentials SHALL be stored in `token.json` in the working directory. The cleanup script SHALL load this token on each run and automatically refresh it using the stored refresh token if the access token is expired, without any user interaction.

#### Scenario: Access token is expired
- **WHEN** `clean_history.py` is run and the access token in `token.json` is expired
- **THEN** the script refreshes the token automatically and proceeds without prompting the user

#### Scenario: Token file is missing when cleanup runs
- **WHEN** `clean_history.py` is run and `token.json` does not exist
- **THEN** the script exits with a clear error message instructing the user to run `auth.py` first

### Requirement: Minimal OAuth scope
The OAuth authorization SHALL request only the `https://www.googleapis.com/auth/youtube.force-ssl` scope, which is the minimum required to read and modify the watch history playlist.

#### Scenario: Scope is limited to YouTube
- **WHEN** the user approves the device flow authorization
- **THEN** the granted token is scoped only to YouTube and cannot access other Google services
