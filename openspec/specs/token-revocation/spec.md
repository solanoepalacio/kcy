## ADDED Requirements

### Requirement: Server-side token revocation
`revoke.py` SHALL revoke the OAuth token by sending a POST request to Google's revocation endpoint (`https://oauth2.googleapis.com/revoke`) with the current access token. This invalidates the token on Google's side immediately.

#### Scenario: Token is successfully revoked server-side
- **WHEN** `revoke.py` is run and the revocation request succeeds
- **THEN** the token is invalidated on Google's servers and can no longer be used to access the API

#### Scenario: Revocation request fails (e.g., token already expired)
- **WHEN** the revocation endpoint returns an error
- **THEN** the script prints a warning but still proceeds to delete the local `token.json`

### Requirement: Local token file deletion
After revoking server-side, `revoke.py` SHALL delete the local `token.json` file.

#### Scenario: token.json is deleted after revocation
- **WHEN** revocation completes (successfully or with a server-side warning)
- **THEN** `token.json` is deleted from the local filesystem

#### Scenario: token.json does not exist
- **WHEN** `revoke.py` is run and `token.json` is not present
- **THEN** the script prints a message that no token was found and exits cleanly without error
