# __CONNECTOR_NAME__ Connector Plugin Starter

This starter package provides a transport plugin scaffold compatible with
`core.connector_transports.TransportPlugin`.

## Generated identity

- `provider`: `__CONNECTOR_PROVIDER__`
- Python package slug: `__CONNECTOR_SLUG__`

## Integration steps

1. Move this directory under your integration package.
2. Register `__CONNECTOR_NAME_CLASS__TransportPlugin` with `TransportPluginRegistry`.
3. Add provider policy scope rules in your policy pack.
4. Validate with `make connector-plugins` and `make extension-contracts`.
