# Dataset manifests

Store one manifest per downloaded dataset here. Do not commit downloaded data. Each manifest should record source name, snapshot/version, source URI, acquisition date, primary checksum, artifact-level checksums, license note, schema version, label definition, time field, entity fields, feature fields, excluded fields, and split strategy. Machine-readable target and availability contracts live in the `data/` directory as separate flat YAML files.

The planned primary sources are ESA Collision Avoidance Challenge for CDM risk and ESA OPSSAT-AD for telemetry, with NASA SMAP/MSL as the documented fallback.
