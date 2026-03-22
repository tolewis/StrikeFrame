# StrikeFrame v0.5.0 Release Notes

Status: PROJECT COMPLETE

## What shipped
- local render/test/config lane
- config validation + smoke tests
- post-render QA/QC
- Popeye vision review with channel-specific prompts
- Dropbox-backed social-media benchmark dataset
- calibration manifest loader
- calibration eval runner with durable run outputs

## Verification snapshot
- `npm test` passes
- benchmark eval improved from `1/4` to `4/4` expectations met
- known bad internal X asset is rejected
- external paid-social good seeds score `pass/warn` instead of blanket rejection

## Version intent
This release closes the current StrikeFrame project scope. Future work remains backlog, not blocker.
