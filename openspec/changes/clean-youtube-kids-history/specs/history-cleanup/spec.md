## ADDED Requirements

### Requirement: Remove kids-targeted videos from watch history
The script SHALL delete each kids-targeted playlist item from the watch history using the YouTube Data API v3 `playlistItems.delete` endpoint, identified by its playlist item ID (not the video ID).

#### Scenario: Kids video found in history
- **WHEN** a playlist item is classified as kids-targeted
- **THEN** the script calls `playlistItems.delete` with the item's playlist item ID and removes it from the history

#### Scenario: No kids videos found in the time window
- **WHEN** no playlist items within the `--since` window are classified as kids-targeted
- **THEN** the script exits with a message indicating no kids videos were found and no deletions were made

### Requirement: Dry-run mode
The script SHALL support a `--dry-run` flag. When provided, the script SHALL identify kids-targeted videos and print them to stdout but SHALL NOT call `playlistItems.delete` or modify the watch history.

#### Scenario: Dry-run with kids videos present
- **WHEN** `--dry-run` is specified and kids-targeted videos are found
- **THEN** the script prints each video's title and video ID and exits without deleting anything

#### Scenario: Dry-run with no kids videos
- **WHEN** `--dry-run` is specified and no kids-targeted videos are found
- **THEN** the script prints a message indicating no kids videos were found

### Requirement: Run summary
Upon completion, the script SHALL print a summary to stdout indicating how many history items were scanned, how many were identified as kids-targeted, and how many were successfully deleted (or would have been deleted in dry-run mode).

#### Scenario: Successful run with removals
- **WHEN** the script completes a run that removed one or more videos
- **THEN** it prints a summary line such as "Scanned 42 items. Found 3 kids videos. Removed 3."

#### Scenario: Successful run with no removals
- **WHEN** the script completes a run with no kids videos found
- **THEN** it prints a summary line such as "Scanned 42 items. Found 0 kids videos. Nothing removed."
