# GMP_HA_Rest
This is a Docker stack with two containers. It can be used to poll Green Mountain Power for the current power usage on your account.

For this to talk to Home Assistant Properly, some yaml is needed.

1.) An Automation:
```yaml
- alias: Process GMP intervals
  mode: single
  trigger:
  - platform: state
    entity_id: sensor.gmp_raw_usage
  - platform: time_pattern
    minutes: /5
  action:
  - variables:
      intervals: '{{ state_attr(''sensor.gmp_raw_usage'', ''intervals'') | default([])
        }}'
      last: '{{ states(''input_datetime.gmp_last_processed'') }}'
  - choose:
    - conditions: '{{ intervals | length > 0 }}'
      sequence:
      - repeat:
          for_each: '{{ intervals }}'
          sequence:
          - variables:
              ts: '{{ repeat.item.timestamp }}'
              kwh: '{{ repeat.item.usage_kwh }}'
          - condition: template
            value_template: '{{ as_timestamp(ts) | int(0) > as_timestamp(last) | int(0)
              }}

              '
          - service: input_number.set_value
            data:
              entity_id: input_number.gmp_lifetime_energy
              value: "{{\n  (states('input_number.gmp_lifetime_energy') | float(0))\n
                \ + (kwh | float(0))\n}}\n"
          - service: input_datetime.set_datetime
            data:
              entity_id: input_datetime.gmp_last_processed
              datetime: '{{ ts }}'
```
2.) Items for configuration.yaml - Utility Meter details, and some helpers.
```yaml
utility_meter:
  gmp_daily_energy:
    source: sensor.gmp_hourly_kwh
    cycle: daily

  gmp_monthly_energy:
    source: sensor.gmp_hourly_kwh
    cycle: monthly

input_number:
  gmp_lifetime_energy:
    name: GMP Lifetime Energy
    min: 0
    max: 1000000
    step: 0.001

input_datetime:
  gmp_last_processed:
    name: GMP Last Processed Timestamp
    has_date: true
    has_time: true
    initial: '2025-12-01 00:00:00'
```
3.) A Sensor for your sensor.yaml
```yaml
- platform: rest
  name: gmp_raw_usage
  resource: http://<Docker Container>:8000/gmp_usage.json
  scan_interval: 300
  value_template: "{{ value_json.generated_at }}"
  json_attributes:
    - intervals
    - daily_totals
```
