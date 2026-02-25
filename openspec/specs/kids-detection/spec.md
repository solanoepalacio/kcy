## ADDED Requirements

### Requirement: Classify video as kids-targeted using madeForKids flag
The script SHALL classify a video as kids-targeted if and only if the `madeForKids` field on the video's `status` resource is `true`. No other signals (category, channel name, title) SHALL be used for classification.

#### Scenario: Video has madeForKids set to true
- **WHEN** a playlist item's video has `madeForKids: true`
- **THEN** the video is classified as kids-targeted and queued for removal

#### Scenario: Video has madeForKids set to false
- **WHEN** a playlist item's video has `madeForKids: false`
- **THEN** the video is not classified as kids-targeted and is left in the history

#### Scenario: Video has madeForKids not set or null
- **WHEN** a playlist item's video does not have the `madeForKids` field or it is null
- **THEN** the video is not classified as kids-targeted and is left in the history
