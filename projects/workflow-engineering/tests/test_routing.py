"""Tests for decision routing behavior."""

import pytest
from workflow_engineering.routing import (
    DecisionRoute,
    create_plan_for_route,
)


def test_decision_route_accepts_supported_routes() -> None:
    """Supported model outputs should map to application routes."""
    assert DecisionRoute("PURCHASE") is DecisionRoute.PURCHASE
    assert DecisionRoute("CAREER") is DecisionRoute.CAREER
    assert DecisionRoute("TRAVEL") is DecisionRoute.TRAVEL
    assert DecisionRoute("GENERAL") is DecisionRoute.GENERAL


def test_decision_route_rejects_unsupported_route() -> None:
    """Unsupported model outputs should fail validation."""
    with pytest.raises(ValueError):
        DecisionRoute("FINANCIAL")


def test_dispatcher_executes_purchase_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Purchase routing should execute the purchase-specific handler."""

    def fake_purchase_plan(
        decision_understanding: str,
        constraints: str,
        evaluation_criteria: str,
    ) -> str:
        return "purchase-plan"

    monkeypatch.setattr(
        "workflow_engineering.routing.create_purchase_plan",
        fake_purchase_plan,
    )

    result = create_plan_for_route(
        DecisionRoute.PURCHASE,
        "decision",
        "constraints",
        "criteria",
    )

    assert result == "purchase-plan"


def test_dispatcher_executes_career_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Career routing should execute the career-specific handler."""

    def fake_career_plan(
        decision_understanding: str,
        constraints: str,
        evaluation_criteria: str,
    ) -> str:
        return "career-plan"

    monkeypatch.setattr(
        "workflow_engineering.routing.create_career_plan",
        fake_career_plan,
    )

    result = create_plan_for_route(
        DecisionRoute.CAREER,
        "decision",
        "constraints",
        "criteria",
    )

    assert result == "career-plan"


def test_dispatcher_executes_travel_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Travel routing should execute the travel-specific handler."""

    def fake_travel_plan(
        decision_understanding: str,
        constraints: str,
        evaluation_criteria: str,
    ) -> str:
        return "travel-plan"

    monkeypatch.setattr(
        "workflow_engineering.routing.create_travel_plan",
        fake_travel_plan,
    )

    result = create_plan_for_route(
        DecisionRoute.TRAVEL,
        "decision",
        "constraints",
        "criteria",
    )

    assert result == "travel-plan"


def test_dispatcher_executes_general_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """General routing should execute the general-purpose handler."""

    def fake_general_plan(
        decision_understanding: str,
        constraints: str,
        evaluation_criteria: str,
    ) -> str:
        return "general-plan"

    monkeypatch.setattr(
        "workflow_engineering.routing.create_general_plan",
        fake_general_plan,
    )

    result = create_plan_for_route(
        DecisionRoute.GENERAL,
        "decision",
        "constraints",
        "criteria",
    )

    assert result == "general-plan"