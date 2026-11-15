from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from standards_bridge.profiles.specification import DomainRecord, bounded, finite_number, normalized_text


UNIT_FACTORS = {("celsius", "fahrenheit"): (9.0 / 5.0, 32.0), ("fahrenheit", "celsius"): (5.0 / 9.0, -32.0),
                ("kg", "lb"): (2.2046226218, 0.0), ("lb", "kg"): (1.0 / 2.2046226218, 0.0)}


@dataclass(frozen=True)
class MappingResult:
    source: str
    target: str
    value: Any
    confidence: float
    lossy: bool


def canonical_term(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalized_text(value)).strip("_")


def convert_unit(value: float, source: str, target: str) -> float:
    source, target = canonical_term(source), canonical_term(target)
    if source == target:
        return finite_number(value)
    if (source, target) not in UNIT_FACTORS:
        raise ValueError("unsupported unit conversion")
    factor, offset = UNIT_FACTORS[(source, target)]
    if source == "fahrenheit" and target == "celsius":
        return (finite_number(value) + offset) * factor
    return finite_number(value) * factor + offset


def map_field(source: str, target: str, value: Any, aliases: Mapping[str, str]) -> MappingResult:
    canonical_source = canonical_term(source)
    canonical_target = canonical_term(target)
    alias_target = canonical_term(aliases.get(canonical_source, canonical_source))
    exact = alias_target == canonical_target
    token_overlap = len(set(alias_target.split("_")) & set(canonical_target.split("_")))
    token_total = max(1, len(set(alias_target.split("_")) | set(canonical_target.split("_"))))
    confidence = 1.0 if exact else token_overlap / token_total
    return MappingResult(canonical_source, canonical_target, value, confidence, confidence < 0.75)


def conformance_profile(record: DomainRecord) -> dict[str, float]:
    unmapped = max(0.0, finite_number(record.payload.get("unmapped_fields", 0.0)))
    evidence = max(0.0, finite_number(record.payload.get("evidence_items", 0.0)))
    waivers = max(0.0, finite_number(record.payload.get("waiver_count", 0.0)))
    pass_rate = bounded(finite_number(record.payload.get("test_pass_rate", 0.0)))
    coverage = bounded(1.0 - unmapped / max(1.0, unmapped + evidence))
    semantic_loss = bounded(unmapped / max(1.0, evidence + 1.0))
    waiver_dependency = bounded(waivers / max(1.0, evidence))
    return {"mapping_coverage": coverage, "semantic_loss": semantic_loss, "waiver_dependency": waiver_dependency,
            "test_confidence": pass_rate * (1.0 - semantic_loss * 0.4)}


def reuse_matrix(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    markets = {canonical_term(row.payload.get("target_market", "unknown")) for row in rows}
    standards = {canonical_term(row.payload.get("standard_family", "unknown")) for row in rows}
    profiles = [conformance_profile(row) for row in rows]
    return {"market_count": float(len(markets)), "standard_count": float(len(standards)),
            "mean_coverage": sum(item["mapping_coverage"] for item in profiles) / max(1, len(profiles)),
            "repeat_cost": bounded(len(standards) / max(1, len(markets) * 4.0))}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    profile = conformance_profile(record)
    reuse = reuse_matrix(repository.list_records() or [record])
    return {"mapping_coverage_weight": 0.6 + profile["mapping_coverage"] * 0.6,
            "semantic_loss_weight": 0.7 + profile["semantic_loss"] * 0.7,
            "test_confidence_weight": 0.6 + profile["test_confidence"] * 0.5,
            "waiver_dependency_weight": 0.8 + profile["waiver_dependency"] * 0.6,
            "market_reuse_weight": 0.7 + reuse["mean_coverage"] * 0.5}
