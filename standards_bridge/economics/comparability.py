from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from standards_bridge.profiles.specification import DomainRecord, bounded, finite_number
from standards_bridge.mappings.semantic_bridge import UNIT_FACTORS, canonical_term, conformance_profile

COMPARABLE = "comparable"
NOT_COMPARABLE = "not_comparable"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"

LAYERS = (COMPARABLE, NOT_COMPARABLE, INSUFFICIENT_EVIDENCE)

DEFAULT_MIN_EVIDENCE_ITEMS = 1.0
DEFAULT_MIN_MAPPING_COVERAGE = 0.25
DEFAULT_WAIVER_RATE_TOLERANCE = 0.15
DEFAULT_MIN_BRIDGE_ALIASES = 1


def unit_pair(left: DomainRecord, right: DomainRecord) -> tuple[str, str]:
    return (canonical_term(left.payload.get("unit_system", "unknown")),
            canonical_term(right.payload.get("unit_system", "unknown")))


def units_are_compatible(left: DomainRecord, right: DomainRecord) -> bool:
    """A pair is unit-comparable when units match or a registered conversion exists."""
    source, target = unit_pair(left, right)
    if source == target:
        return True
    return (source, target) in UNIT_FACTORS or (target, source) in UNIT_FACTORS


def waiver_rate(record: DomainRecord) -> float:
    waivers = max(0.0, finite_number(record.payload.get("waiver_count", 0.0)))
    evidence = max(1.0, finite_number(record.payload.get("evidence_items", 0.0)))
    return bounded(waivers / evidence)


def evidence_gaps(record: DomainRecord, context: Mapping[str, Any]) -> list[str]:
    """Insufficient-evidence signals, judged from the case payload alone."""
    gaps: list[str] = []
    pass_rate = record.payload.get("test_pass_rate")
    if pass_rate in (None, ""):
        gaps.append("test_pass_rate_missing")
    evidence_items = finite_number(record.payload.get("evidence_items", 0.0))
    if evidence_items < finite_number(context.get("comparability_min_evidence_items", DEFAULT_MIN_EVIDENCE_ITEMS)):
        gaps.append("evidence_items_below_floor")
    profile = conformance_profile(record)
    coverage_floor = finite_number(context.get("comparability_min_mapping_coverage", DEFAULT_MIN_MAPPING_COVERAGE))
    if profile["mapping_coverage"] < coverage_floor:
        gaps.append("mapping_coverage_below_floor")
    return gaps


def build_mapping_graph(mapping_rows: Iterable[Mapping[str, Any]]) -> dict[str, set[str]]:
    """Undirected graph of standard families connected by registered mappings."""
    graph: dict[str, set[str]] = defaultdict(set)
    for row in mapping_rows:
        source = canonical_term(row["source_standard"])
        target = canonical_term(row["target_standard"])
        if not source or not target:
            continue
        graph[source].add(target)
        graph[target].add(source)
    return graph


def bridge_quality(mapping_rows: Iterable[Mapping[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """Alias coverage of every directed standard-family bridge under the current revision.

    A mapping revision that shrinks the alias table therefore weakens the bridge
    connecting two families, which can move a cross-family comparison out of the
    comparable layer even though the graph edge itself still exists.
    """
    bridges: dict[tuple[str, str], dict[str, Any]] = {}
    for row in mapping_rows:
        source = canonical_term(row["source_standard"])
        target = canonical_term(row["target_standard"])
        aliases = row.get("aliases")
        if aliases is None:
            raw = row.get("mapping_json")
            aliases = json.loads(raw) if isinstance(raw, str) else {}
        if not isinstance(aliases, Mapping):
            aliases = {}
        bridges[(source, target)] = {"aliases": dict(aliases), "alias_count": len(aliases),
                                     "revision": row.get("revision", 1)}
        bridges[(target, source)] = {"aliases": dict(aliases), "alias_count": len(aliases),
                                     "revision": row.get("revision", 1)}
    return bridges


def standards_are_connected(left_family: str, right_family: str,
                            graph: Mapping[str, set[str]],
                            blocked_edges: set[tuple[str, str]] | None = None) -> bool:
    blocked_edges = blocked_edges or set()
    start = canonical_term(left_family)
    goal = canonical_term(right_family)
    if start == goal:
        return True
    seen = {start}
    queue = [start]
    while queue:
        current = queue.pop()
        for neighbour in graph.get(current, ()):  # type: ignore[union-attr]
            edge = tuple(sorted((current, neighbour)))
            if edge in blocked_edges:
                continue
            if neighbour == goal:
                return True
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return False


def assess_pair(left: DomainRecord, right: DomainRecord,
                mapping_graph: Mapping[str, set[str]] | None = None,
                context: Mapping[str, Any] | None = None,
                bridges: Mapping[tuple[str, str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Classify one cross-market pair without pooling unlike units or waiver calibers."""
    context = context or {}
    mapping_graph = mapping_graph or {}
    bridges = bridges or {}
    reasons: list[str] = []

    gaps = sorted(set(evidence_gaps(left, context) + evidence_gaps(right, context)))
    if gaps:
        return {"left": left.record_id, "right": right.record_id, "layer": INSUFFICIENT_EVIDENCE,
                "reasons": gaps, "unit_pair": list(unit_pair(left, right)),
                "waiver_rates": {left.record_id: waiver_rate(left), right.record_id: waiver_rate(right)}}

    if not units_are_compatible(left, right):
        reasons.append("unit_systems_not_convertible")
        return {"left": left.record_id, "right": right.record_id, "layer": NOT_COMPARABLE,
                "reasons": reasons, "unit_pair": list(unit_pair(left, right)),
                "waiver_rates": {left.record_id: waiver_rate(left), right.record_id: waiver_rate(right)}}

    left_family = canonical_term(left.payload.get("standard_family", "unknown"))
    right_family = canonical_term(right.payload.get("standard_family", "unknown"))
    min_aliases = max(1, int(finite_number(context.get("comparability_min_bridge_aliases", DEFAULT_MIN_BRIDGE_ALIASES))))
    blocked = {edge for edge, quality in bridges.items() if quality["alias_count"] < min_aliases}
    blocked = {tuple(sorted(edge)) for edge in blocked}
    connected = standards_are_connected(str(left_family), str(right_family), mapping_graph, blocked)
    if not connected:
        existing_edge = bridges.get((left_family, right_family))
        if existing_edge is not None and existing_edge["alias_count"] < min_aliases:
            reasons.append("mapping_bridge_alias_coverage_insufficient")
        else:
            reasons.append("no_mapping_path_between_standard_families")

    tolerance = finite_number(context.get("waiver_rate_tolerance", DEFAULT_WAIVER_RATE_TOLERANCE))
    left_rate = waiver_rate(left)
    right_rate = waiver_rate(right)
    if abs(left_rate - right_rate) > tolerance:
        reasons.append("waiver_caliber_diverges")

    layer = COMPARABLE if not reasons else NOT_COMPARABLE
    return {"left": left.record_id, "right": right.record_id, "layer": layer,
            "reasons": reasons, "unit_pair": list(unit_pair(left, right)),
            "waiver_rates": {left.record_id: left_rate, right.record_id: right_rate}}


def stratified_pass_rates(records: Sequence[DomainRecord],
                          mapping_graph: Mapping[str, set[str]] | None = None,
                          context: Mapping[str, Any] | None = None,
                          bridges: Mapping[tuple[str, str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Average pass rate only inside a comparability layer; the pooled mean is never reused.

    Every pair is assessed pairwise. A case enters the comparable layer only when
    at least one direct comparable partner exists; comparability is never inferred
    transitively. Otherwise each case lands in the strongest blocking layer, with
    insufficient evidence taking precedence over not-comparable because missing
    evidence cannot justify a hard block.
    """
    pair_rows: list[dict[str, Any]] = []
    if not records:
        return {"layers": {layer: {"case_count": 0, "mean_pass_rate": 0.0, "case_ids": []}
                           for layer in LAYERS},
                "pairs": pair_rows, "pooled_mean_pass_rate": 0.0, "pooled_case_count": 0}

    comparable_partners: dict[str, set[str]] = defaultdict(set)
    insufficient: set[str] = set()
    not_comparable: set[str] = set()
    by_id = {record.record_id: record for record in records}
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            row = assess_pair(left, right, mapping_graph, context, bridges)
            pair_rows.append(row)
            if row["layer"] == COMPARABLE:
                # comparability holds pairwise; it is never inferred transitively
                comparable_partners[left.record_id].add(right.record_id)
                comparable_partners[right.record_id].add(left.record_id)
            elif row["layer"] == INSUFFICIENT_EVIDENCE:
                insufficient.update((left.record_id, right.record_id))
            else:
                not_comparable.update((left.record_id, right.record_id))

    strata: dict[str, list[DomainRecord]] = {layer: [] for layer in LAYERS}
    for record in records:
        if comparable_partners.get(record.record_id):
            layer = COMPARABLE
        elif record.record_id in insufficient:
            layer = INSUFFICIENT_EVIDENCE
        else:
            layer = NOT_COMPARABLE
        strata[layer].append(record)

    def mean_pass_rate(rows: Sequence[DomainRecord]) -> float:
        rates = [finite_number(row.payload.get("test_pass_rate", 0.0)) for row in rows
                 if row.payload.get("test_pass_rate") not in (None, "")]
        return sum(rates) / len(rates) if rates else 0.0

    layers = {layer: {"case_count": len(rows), "mean_pass_rate": mean_pass_rate(rows),
                      "case_ids": [row.record_id for row in rows]}
              for layer, rows in strata.items()}
    pooled = [row for row in records if row.payload.get("test_pass_rate") not in (None, "")]
    return {"layers": layers, "pairs": pair_rows,
            "pooled_mean_pass_rate": mean_pass_rate(pooled), "pooled_case_count": len(pooled)}


def reuse_eligibility(records: Sequence[DomainRecord],
                      mapping_graph: Mapping[str, set[str]] | None = None,
                      context: Mapping[str, Any] | None = None,
                      blocked_case_ids: Iterable[str] = (),
                      bridges: Mapping[tuple[str, str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Reuse judgement per case, driven only by genuinely comparable evidence."""
    blocked = set(blocked_case_ids)
    pair_rows: list[dict[str, Any]] = []
    support: dict[str, list[str]] = defaultdict(list)
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            row = assess_pair(left, right, mapping_graph, context, bridges)
            pair_rows.append(row)
            if row["layer"] == COMPARABLE:
                support[left.record_id].append(right.record_id)
                support[right.record_id].append(left.record_id)

    cases: dict[str, dict[str, Any]] = {}
    for record in records:
        own_pairs = [row for row in pair_rows if record.record_id in (row["left"], row["right"])]
        not_comparable_reasons = sorted({reason for row in own_pairs if row["layer"] == NOT_COMPARABLE
                                         for reason in row["reasons"]})
        insufficient_reasons = sorted({reason for row in own_pairs if row["layer"] == INSUFFICIENT_EVIDENCE
                                       for reason in row["reasons"]})
        if record.record_id in blocked:
            status = "revalidation_pending"
            reasons = ["mapping_revision_waits_for_revalidation"]
        elif support.get(record.record_id):
            status = "reuse_supported"
            reasons = ["comparable_evidence_available"]
        elif len(records) < 2:
            status = "insufficient_evidence"
            reasons = ["single_case_portfolio"]
        elif insufficient_reasons:
            status = "insufficient_evidence"
            reasons = insufficient_reasons
        else:
            status = "not_comparable"
            reasons = not_comparable_reasons or ["no_comparable_partner"]
        cases[record.record_id] = {"status": status, "reasons": reasons,
                                   "comparable_partners": sorted(support.get(record.record_id, ()))}
    counts = {layer: sum(1 for item in cases.values() if item["status"] == layer)
              for layer in ("reuse_supported", "not_comparable", "insufficient_evidence", "revalidation_pending")}
    return {"cases": cases, "pairs": pair_rows, "counts": counts}
