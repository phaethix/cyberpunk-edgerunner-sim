# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added

- Web-based single-page game UI (Vanilla JS + Tailwind) served by a FastAPI backend.
- Eight gigs with risk-tiered rewards and failure penalties.
- Six installable cyberware upgrades with combat bonuses and humanity costs.
- Recovery actions: Trauma Team heal and safehouse rest.
- Game-state API endpoints (`/api/status`, `/api/gig`, `/api/buy`,
  `/api/uninstall`, `/api/heal`, `/api/rest`, `/api/restart`).
- Original terminal text-adventure version (`cyberpunk.py`).
- Hugging Face Spaces deployment via Docker SDK.
- Comprehensive unit tests for core game logic.

[1.0.0]: https://github.com/phaethix/cyberpunk-edgerunner-sim/releases/tag/v1.0.0
