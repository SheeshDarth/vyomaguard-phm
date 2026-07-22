from vymoa_guard_phm.features.telemetry import robust_channel_scores


def test_telemetry_anomaly_localizes_channel():
    rows = [
        {"timestamp": "1", "channel": "stable", "value": 1.0},
        {"timestamp": "2", "channel": "stable", "value": 1.1},
        {"timestamp": "3", "channel": "stable", "value": 0.9},
        {"timestamp": "1", "channel": "faulty", "value": 1.0},
        {"timestamp": "2", "channel": "faulty", "value": 1.1},
        {"timestamp": "3", "channel": "faulty", "value": 8.0},
    ]
    score, channels, window, _ = robust_channel_scores(rows)
    assert score > 0.65
    assert "faulty" in channels
    assert window["channels"] == channels

