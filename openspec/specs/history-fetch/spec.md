## ADDED Requirements

### Requirement: Fetch watch history playlist items
The script SHALL retrieve playlist items from the authenticated user's watch history playlist using the YouTube Data API v3 `playlistItems.list` endpoint. It SHALL request the `snippet` and `status` parts for each item to retrieve video metadata and the `madeForKids` flag in a single API call.

#### Scenario: History playlist exists and has items
- **WHEN** the script fetches the watch history playlist
- **THEN** it returns a list of playlist items each containing at least the video ID, title, `publishedAt` timestamp, and `madeForKids` flag

#### Scenario: Watch history playlist not found
- **WHEN** the authenticated user's account does not expose a watch history playlist
- **THEN** the script exits with a clear error message explaining that the history playlist was not found and that the account may not support this feature

### Requirement: Pagination
The script SHALL handle paginated responses from `playlistItems.list` using `nextPageToken`, fetching all pages required to cover the requested time window.

#### Scenario: History spans multiple pages
- **WHEN** the watch history contains more items than fit in a single API response
- **THEN** the script follows `nextPageToken` values until all items within the `--since` window have been retrieved

#### Scenario: All items on first page are older than the window
- **WHEN** a page is retrieved and all items have a `publishedAt` timestamp older than the `--since` cutoff
- **THEN** the script stops paginating and does not fetch further pages

### Requirement: Time window filtering
The script SHALL accept a `--since` argument (e.g., `1h`, `3h`, `12h`, `1d`) and only process history items with a `publishedAt` timestamp within that window relative to the time of execution. Items older than the window SHALL be ignored.

#### Scenario: Items within the time window
- **WHEN** an item's `publishedAt` timestamp is within the duration specified by `--since`
- **THEN** the item is included for kids-detection processing

#### Scenario: Items outside the time window
- **WHEN** an item's `publishedAt` timestamp is older than the duration specified by `--since`
- **THEN** the item is excluded from processing
