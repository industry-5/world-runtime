from core.observability import ObservabilityStore


def test_observability_records_events_and_traces():
    store = ObservabilityStore()

    trace_id = store.start_trace(
        name="test.trace",
        component="test",
        context={"case": "basic"},
    )
    store.trace_event(trace_id, "checkpoint", {"step": 1})
    store.emit(component="test", event_type="custom.event", trace_id=trace_id)
    store.finish_trace(trace_id, status="completed")

    summary = store.summary()
    assert summary["totals"]["events"] >= 3
    assert summary["totals"]["traces"] == 1
    assert summary["events"]["by_component"]["test"] >= 3

    traces = store.list_traces()
    assert traces[0]["trace_id"] == trace_id
    assert traces[0]["status"] == "completed"


def test_dashboard_includes_slow_trace_panel():
    store = ObservabilityStore()

    trace_id = store.start_trace(name="dashboard.trace", component="test")
    store.finish_trace(trace_id, status="completed")

    dashboard = store.dashboard()
    assert dashboard["cards"]["traces"] == 1
    assert "slow_traces" in dashboard
