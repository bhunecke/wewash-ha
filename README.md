# WeWash for Home Assistant

Integrates [WeWash](https://we-wash.com) laundry room availability into Home Assistant.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bhunecke&repository=wewash-ha)

## Setup

1. Install via HACS
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → WeWash
4. Paste your `ww_refresh` cookie from app.we-wash.com

## Getting your refresh token

1. Open [app.we-wash.com](https://app.we-wash.com) and log in
2. Open DevTools → Application → Cookies → `https://app.we-wash.com`
3. Copy the value of `ww_refresh`
