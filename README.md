# KSP Price Tracker for Home Assistant

A Home Assistant integration that tracks prices from KSP

## ⚠️ Disclaimer ⚠️

This is a non-commercial, personal project created for tracking KSP item prices. The project is not affiliated with or endorsed by KSP (or any related companies). It is intended for educational and personal use only. If KSP or any associated party has concerns or wishes for this project to be taken down, please contact me via email, and I will take the necessary action.

---
![chrome_YLE5HwzSoe](https://github.com/user-attachments/assets/dcb791e9-8f28-4b92-a401-bf7bb4f65ec0)

https://github.com/user-attachments/assets/dca7ca50-9a79-45d3-b56d-771a8c48465b

---

## Features

- Tracks various attributes for items, including regular price, Eilat price, and product name
- Automatic price updates at configurable intervals
- Manual refresh option via service call
- Displays product name and pricing information
- Easy configuration through Home Assistant UI

## Installation

### Manual Installation (HACS not yet supported)

1. Copy the `ksp_price_tracker` folder from `custom_components` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click the "+ ADD INTEGRATION" button
5. Search for "KSP Price Tracker"

### Configuration

During setup, you'll need to provide:
- Item ID (can be found in the KSP product URL, e.g., 350617 from https://website/web/item/350617)
- Update interval in minutes (optional, defaults to 60 minutes)

## Services

### ksp_price_tracker.refresh_price

Manually refresh the price data for one or all items.

Service data:
```yaml
item_id: "350617"  # Optional. If not provided, refreshes all items
```

Example usage in automation:
```yaml
service: ksp_price_tracker.refresh_price
data:
  item_id: "350617"
```

Example button card configuration:
```yaml
type: button
tap_action:
  action: call-service
  service: ksp_price_tracker.refresh_price
  service_data:
    item_id: "350617"
name: Refresh KSP Price
```

## Example Automations

### Price Drop Alert
```yaml
alias: "KSP Price Drop Alert"
description: "Send notification when price drops below threshold"
trigger:
  - platform: numeric_state
    entity_id: sensor.ksp_price
    below: 1000
action:
  - service: notify.mobile_app
    data:
      title: "Price Drop Alert!"
      message: "{{ states.sensor.ksp_price.attributes.item_name }} is now {{ states.sensor.ksp_price.state }} ILS"
```

### Regular Price Check
```yaml
alias: "Check KSP Price Every Morning"
trigger:
  - platform: time
    at: "09:00:00"
action:
  - service: ksp_price_tracker.refresh_price
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
