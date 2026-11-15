from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from standards_bridge.profiles.specification import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_target_market_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_target_market_presence_threshold', 10.333)
    return _result('check_target_market_presence', adjusted, threshold, True, 'validates target_market presence',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_target_market_range_threshold', 12.667)
    return _result('check_target_market_range', adjusted, threshold, True, 'validates target_market range',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_target_market_stability_threshold', 15.0)
    return _result('check_target_market_stability', adjusted, threshold, False, 'validates target_market stability',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_target_market_freshness_threshold', 17.333)
    return _result('check_target_market_freshness', adjusted, threshold, True, 'validates target_market freshness',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_target_market_coverage_threshold', 19.667)
    return _result('check_target_market_coverage', adjusted, threshold, True, 'validates target_market coverage',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_target_market_consistency_threshold', 22.0)
    return _result('check_target_market_consistency', adjusted, threshold, False, 'validates target_market consistency',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_target_market_risk_threshold', 24.333)
    return _result('check_target_market_risk', adjusted, threshold, True, 'validates target_market risk',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_target_market_confidence_threshold', 26.667)
    return _result('check_target_market_confidence', adjusted, threshold, True, 'validates target_market confidence',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_target_market_dependency_threshold', 29.0)
    return _result('check_target_market_dependency', adjusted, threshold, False, 'validates target_market dependency',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_market_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_market')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_target_market_readiness_threshold', 31.333)
    return _result('check_target_market_readiness', adjusted, threshold, True, 'validates target_market readiness',
                   {'field': 'target_market', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_standard_family_presence_threshold', 9.333)
    return _result('check_standard_family_presence', adjusted, threshold, True, 'validates standard_family presence',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_standard_family_range_threshold', 11.667)
    return _result('check_standard_family_range', adjusted, threshold, False, 'validates standard_family range',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_standard_family_stability_threshold', 14.0)
    return _result('check_standard_family_stability', adjusted, threshold, True, 'validates standard_family stability',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_standard_family_freshness_threshold', 16.333)
    return _result('check_standard_family_freshness', adjusted, threshold, True, 'validates standard_family freshness',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_standard_family_coverage_threshold', 18.667)
    return _result('check_standard_family_coverage', adjusted, threshold, False, 'validates standard_family coverage',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_standard_family_consistency_threshold', 21.0)
    return _result('check_standard_family_consistency', adjusted, threshold, True, 'validates standard_family consistency',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_standard_family_risk_threshold', 23.333)
    return _result('check_standard_family_risk', adjusted, threshold, True, 'validates standard_family risk',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_standard_family_confidence_threshold', 25.667)
    return _result('check_standard_family_confidence', adjusted, threshold, False, 'validates standard_family confidence',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_standard_family_dependency_threshold', 28.0)
    return _result('check_standard_family_dependency', adjusted, threshold, True, 'validates standard_family dependency',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_standard_family_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'standard_family')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_standard_family_readiness_threshold', 30.333)
    return _result('check_standard_family_readiness', adjusted, threshold, True, 'validates standard_family readiness',
                   {'field': 'standard_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_schema_version_presence_threshold', 8.333)
    return _result('check_schema_version_presence', adjusted, threshold, False, 'validates schema_version presence',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_schema_version_range_threshold', 10.667)
    return _result('check_schema_version_range', adjusted, threshold, True, 'validates schema_version range',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_schema_version_stability_threshold', 13.0)
    return _result('check_schema_version_stability', adjusted, threshold, True, 'validates schema_version stability',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_schema_version_freshness_threshold', 15.333)
    return _result('check_schema_version_freshness', adjusted, threshold, False, 'validates schema_version freshness',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_schema_version_coverage_threshold', 17.667)
    return _result('check_schema_version_coverage', adjusted, threshold, True, 'validates schema_version coverage',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_schema_version_consistency_threshold', 20.0)
    return _result('check_schema_version_consistency', adjusted, threshold, True, 'validates schema_version consistency',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_schema_version_risk_threshold', 22.333)
    return _result('check_schema_version_risk', adjusted, threshold, False, 'validates schema_version risk',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_schema_version_confidence_threshold', 24.667)
    return _result('check_schema_version_confidence', adjusted, threshold, True, 'validates schema_version confidence',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_schema_version_dependency_threshold', 27.0)
    return _result('check_schema_version_dependency', adjusted, threshold, True, 'validates schema_version dependency',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_schema_version_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'schema_version')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_schema_version_readiness_threshold', 29.333)
    return _result('check_schema_version_readiness', adjusted, threshold, False, 'validates schema_version readiness',
                   {'field': 'schema_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_unit_system_presence_threshold', 31.667)
    return _result('check_unit_system_presence', adjusted, threshold, True, 'validates unit_system presence',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_unit_system_range_threshold', 9.667)
    return _result('check_unit_system_range', adjusted, threshold, True, 'validates unit_system range',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_unit_system_stability_threshold', 12.0)
    return _result('check_unit_system_stability', adjusted, threshold, False, 'validates unit_system stability',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_unit_system_freshness_threshold', 14.333)
    return _result('check_unit_system_freshness', adjusted, threshold, True, 'validates unit_system freshness',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_unit_system_coverage_threshold', 16.667)
    return _result('check_unit_system_coverage', adjusted, threshold, True, 'validates unit_system coverage',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_unit_system_consistency_threshold', 19.0)
    return _result('check_unit_system_consistency', adjusted, threshold, False, 'validates unit_system consistency',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_unit_system_risk_threshold', 21.333)
    return _result('check_unit_system_risk', adjusted, threshold, True, 'validates unit_system risk',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_unit_system_confidence_threshold', 23.667)
    return _result('check_unit_system_confidence', adjusted, threshold, True, 'validates unit_system confidence',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_unit_system_dependency_threshold', 26.0)
    return _result('check_unit_system_dependency', adjusted, threshold, False, 'validates unit_system dependency',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unit_system_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unit_system')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_unit_system_readiness_threshold', 28.333)
    return _result('check_unit_system_readiness', adjusted, threshold, True, 'validates unit_system readiness',
                   {'field': 'unit_system', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_language_pack_presence_threshold', 30.667)
    return _result('check_language_pack_presence', adjusted, threshold, True, 'validates language_pack presence',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_language_pack_range_threshold', 8.667)
    return _result('check_language_pack_range', adjusted, threshold, False, 'validates language_pack range',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_language_pack_stability_threshold', 11.0)
    return _result('check_language_pack_stability', adjusted, threshold, True, 'validates language_pack stability',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_language_pack_freshness_threshold', 13.333)
    return _result('check_language_pack_freshness', adjusted, threshold, True, 'validates language_pack freshness',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_language_pack_coverage_threshold', 15.667)
    return _result('check_language_pack_coverage', adjusted, threshold, False, 'validates language_pack coverage',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_language_pack_consistency_threshold', 18.0)
    return _result('check_language_pack_consistency', adjusted, threshold, True, 'validates language_pack consistency',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_language_pack_risk_threshold', 20.333)
    return _result('check_language_pack_risk', adjusted, threshold, True, 'validates language_pack risk',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_language_pack_confidence_threshold', 22.667)
    return _result('check_language_pack_confidence', adjusted, threshold, False, 'validates language_pack confidence',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_language_pack_dependency_threshold', 25.0)
    return _result('check_language_pack_dependency', adjusted, threshold, True, 'validates language_pack dependency',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_pack_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_pack')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_language_pack_readiness_threshold', 27.333)
    return _result('check_language_pack_readiness', adjusted, threshold, True, 'validates language_pack readiness',
                   {'field': 'language_pack', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_privacy_tier_presence_threshold', 29.667)
    return _result('check_privacy_tier_presence', adjusted, threshold, False, 'validates privacy_tier presence',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_privacy_tier_range_threshold', 32.0)
    return _result('check_privacy_tier_range', adjusted, threshold, True, 'validates privacy_tier range',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_privacy_tier_stability_threshold', 10.0)
    return _result('check_privacy_tier_stability', adjusted, threshold, True, 'validates privacy_tier stability',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_privacy_tier_freshness_threshold', 12.333)
    return _result('check_privacy_tier_freshness', adjusted, threshold, False, 'validates privacy_tier freshness',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_privacy_tier_coverage_threshold', 14.667)
    return _result('check_privacy_tier_coverage', adjusted, threshold, True, 'validates privacy_tier coverage',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_privacy_tier_consistency_threshold', 17.0)
    return _result('check_privacy_tier_consistency', adjusted, threshold, True, 'validates privacy_tier consistency',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_privacy_tier_risk_threshold', 19.333)
    return _result('check_privacy_tier_risk', adjusted, threshold, False, 'validates privacy_tier risk',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_privacy_tier_confidence_threshold', 21.667)
    return _result('check_privacy_tier_confidence', adjusted, threshold, True, 'validates privacy_tier confidence',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_privacy_tier_dependency_threshold', 24.0)
    return _result('check_privacy_tier_dependency', adjusted, threshold, True, 'validates privacy_tier dependency',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_privacy_tier_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'privacy_tier')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_privacy_tier_readiness_threshold', 26.333)
    return _result('check_privacy_tier_readiness', adjusted, threshold, False, 'validates privacy_tier readiness',
                   {'field': 'privacy_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_safety_threshold_presence_threshold', 28.667)
    return _result('check_safety_threshold_presence', adjusted, threshold, True, 'validates safety_threshold presence',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_safety_threshold_range_threshold', 31.0)
    return _result('check_safety_threshold_range', adjusted, threshold, True, 'validates safety_threshold range',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_safety_threshold_stability_threshold', 9.0)
    return _result('check_safety_threshold_stability', adjusted, threshold, False, 'validates safety_threshold stability',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_safety_threshold_freshness_threshold', 11.333)
    return _result('check_safety_threshold_freshness', adjusted, threshold, True, 'validates safety_threshold freshness',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_safety_threshold_coverage_threshold', 13.667)
    return _result('check_safety_threshold_coverage', adjusted, threshold, True, 'validates safety_threshold coverage',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_safety_threshold_consistency_threshold', 16.0)
    return _result('check_safety_threshold_consistency', adjusted, threshold, False, 'validates safety_threshold consistency',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_safety_threshold_risk_threshold', 18.333)
    return _result('check_safety_threshold_risk', adjusted, threshold, True, 'validates safety_threshold risk',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_safety_threshold_confidence_threshold', 20.667)
    return _result('check_safety_threshold_confidence', adjusted, threshold, True, 'validates safety_threshold confidence',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_safety_threshold_dependency_threshold', 23.0)
    return _result('check_safety_threshold_dependency', adjusted, threshold, False, 'validates safety_threshold dependency',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_safety_threshold_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'safety_threshold')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_safety_threshold_readiness_threshold', 25.333)
    return _result('check_safety_threshold_readiness', adjusted, threshold, True, 'validates safety_threshold readiness',
                   {'field': 'safety_threshold', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_evidence_items_presence_threshold', 27.667)
    return _result('check_evidence_items_presence', adjusted, threshold, True, 'validates evidence_items presence',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_evidence_items_range_threshold', 30.0)
    return _result('check_evidence_items_range', adjusted, threshold, False, 'validates evidence_items range',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_evidence_items_stability_threshold', 8.0)
    return _result('check_evidence_items_stability', adjusted, threshold, True, 'validates evidence_items stability',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_evidence_items_freshness_threshold', 10.333)
    return _result('check_evidence_items_freshness', adjusted, threshold, True, 'validates evidence_items freshness',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_evidence_items_coverage_threshold', 12.667)
    return _result('check_evidence_items_coverage', adjusted, threshold, False, 'validates evidence_items coverage',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_evidence_items_consistency_threshold', 15.0)
    return _result('check_evidence_items_consistency', adjusted, threshold, True, 'validates evidence_items consistency',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_evidence_items_risk_threshold', 17.333)
    return _result('check_evidence_items_risk', adjusted, threshold, True, 'validates evidence_items risk',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_evidence_items_confidence_threshold', 19.667)
    return _result('check_evidence_items_confidence', adjusted, threshold, False, 'validates evidence_items confidence',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_evidence_items_dependency_threshold', 22.0)
    return _result('check_evidence_items_dependency', adjusted, threshold, True, 'validates evidence_items dependency',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_items_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_items')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_evidence_items_readiness_threshold', 24.333)
    return _result('check_evidence_items_readiness', adjusted, threshold, True, 'validates evidence_items readiness',
                   {'field': 'evidence_items', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_unmapped_fields_presence_threshold', 26.667)
    return _result('check_unmapped_fields_presence', adjusted, threshold, False, 'validates unmapped_fields presence',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_unmapped_fields_range_threshold', 29.0)
    return _result('check_unmapped_fields_range', adjusted, threshold, True, 'validates unmapped_fields range',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_unmapped_fields_stability_threshold', 31.333)
    return _result('check_unmapped_fields_stability', adjusted, threshold, True, 'validates unmapped_fields stability',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_unmapped_fields_freshness_threshold', 9.333)
    return _result('check_unmapped_fields_freshness', adjusted, threshold, False, 'validates unmapped_fields freshness',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_unmapped_fields_coverage_threshold', 11.667)
    return _result('check_unmapped_fields_coverage', adjusted, threshold, True, 'validates unmapped_fields coverage',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_unmapped_fields_consistency_threshold', 14.0)
    return _result('check_unmapped_fields_consistency', adjusted, threshold, True, 'validates unmapped_fields consistency',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_unmapped_fields_risk_threshold', 16.333)
    return _result('check_unmapped_fields_risk', adjusted, threshold, False, 'validates unmapped_fields risk',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_unmapped_fields_confidence_threshold', 18.667)
    return _result('check_unmapped_fields_confidence', adjusted, threshold, True, 'validates unmapped_fields confidence',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_unmapped_fields_dependency_threshold', 21.0)
    return _result('check_unmapped_fields_dependency', adjusted, threshold, True, 'validates unmapped_fields dependency',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unmapped_fields_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unmapped_fields')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_unmapped_fields_readiness_threshold', 23.333)
    return _result('check_unmapped_fields_readiness', adjusted, threshold, False, 'validates unmapped_fields readiness',
                   {'field': 'unmapped_fields', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_waiver_count_presence_threshold', 25.667)
    return _result('check_waiver_count_presence', adjusted, threshold, True, 'validates waiver_count presence',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_waiver_count_range_threshold', 28.0)
    return _result('check_waiver_count_range', adjusted, threshold, True, 'validates waiver_count range',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_waiver_count_stability_threshold', 30.333)
    return _result('check_waiver_count_stability', adjusted, threshold, False, 'validates waiver_count stability',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_waiver_count_freshness_threshold', 8.333)
    return _result('check_waiver_count_freshness', adjusted, threshold, True, 'validates waiver_count freshness',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_waiver_count_coverage_threshold', 10.667)
    return _result('check_waiver_count_coverage', adjusted, threshold, True, 'validates waiver_count coverage',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_waiver_count_consistency_threshold', 13.0)
    return _result('check_waiver_count_consistency', adjusted, threshold, False, 'validates waiver_count consistency',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_waiver_count_risk_threshold', 15.333)
    return _result('check_waiver_count_risk', adjusted, threshold, True, 'validates waiver_count risk',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_waiver_count_confidence_threshold', 17.667)
    return _result('check_waiver_count_confidence', adjusted, threshold, True, 'validates waiver_count confidence',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_waiver_count_dependency_threshold', 20.0)
    return _result('check_waiver_count_dependency', adjusted, threshold, False, 'validates waiver_count dependency',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_waiver_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'waiver_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_waiver_count_readiness_threshold', 22.333)
    return _result('check_waiver_count_readiness', adjusted, threshold, True, 'validates waiver_count readiness',
                   {'field': 'waiver_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_test_pass_rate_presence_threshold', 24.667)
    return _result('check_test_pass_rate_presence', adjusted, threshold, True, 'validates test_pass_rate presence',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_test_pass_rate_range_threshold', 27.0)
    return _result('check_test_pass_rate_range', adjusted, threshold, False, 'validates test_pass_rate range',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_test_pass_rate_stability_threshold', 29.333)
    return _result('check_test_pass_rate_stability', adjusted, threshold, True, 'validates test_pass_rate stability',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_test_pass_rate_freshness_threshold', 31.667)
    return _result('check_test_pass_rate_freshness', adjusted, threshold, True, 'validates test_pass_rate freshness',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_test_pass_rate_coverage_threshold', 9.667)
    return _result('check_test_pass_rate_coverage', adjusted, threshold, False, 'validates test_pass_rate coverage',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_test_pass_rate_consistency_threshold', 12.0)
    return _result('check_test_pass_rate_consistency', adjusted, threshold, True, 'validates test_pass_rate consistency',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_test_pass_rate_risk_threshold', 14.333)
    return _result('check_test_pass_rate_risk', adjusted, threshold, True, 'validates test_pass_rate risk',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_test_pass_rate_confidence_threshold', 16.667)
    return _result('check_test_pass_rate_confidence', adjusted, threshold, False, 'validates test_pass_rate confidence',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_test_pass_rate_dependency_threshold', 19.0)
    return _result('check_test_pass_rate_dependency', adjusted, threshold, True, 'validates test_pass_rate dependency',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_test_pass_rate_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'test_pass_rate')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_test_pass_rate_readiness_threshold', 21.333)
    return _result('check_test_pass_rate_readiness', adjusted, threshold, True, 'validates test_pass_rate readiness',
                   {'field': 'test_pass_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_local_partner_presence_threshold', 23.667)
    return _result('check_local_partner_presence', adjusted, threshold, False, 'validates local_partner presence',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_local_partner_range_threshold', 26.0)
    return _result('check_local_partner_range', adjusted, threshold, True, 'validates local_partner range',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_local_partner_stability_threshold', 28.333)
    return _result('check_local_partner_stability', adjusted, threshold, True, 'validates local_partner stability',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_local_partner_freshness_threshold', 30.667)
    return _result('check_local_partner_freshness', adjusted, threshold, False, 'validates local_partner freshness',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_local_partner_coverage_threshold', 8.667)
    return _result('check_local_partner_coverage', adjusted, threshold, True, 'validates local_partner coverage',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_local_partner_consistency_threshold', 11.0)
    return _result('check_local_partner_consistency', adjusted, threshold, True, 'validates local_partner consistency',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_local_partner_risk_threshold', 13.333)
    return _result('check_local_partner_risk', adjusted, threshold, False, 'validates local_partner risk',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_local_partner_confidence_threshold', 15.667)
    return _result('check_local_partner_confidence', adjusted, threshold, True, 'validates local_partner confidence',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_local_partner_dependency_threshold', 18.0)
    return _result('check_local_partner_dependency', adjusted, threshold, True, 'validates local_partner dependency',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_local_partner_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'local_partner')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_local_partner_readiness_threshold', 20.333)
    return _result('check_local_partner_readiness', adjusted, threshold, False, 'validates local_partner readiness',
                   {'field': 'local_partner', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_target_market_presence,
    check_target_market_range,
    check_target_market_stability,
    check_target_market_freshness,
    check_target_market_coverage,
    check_target_market_consistency,
    check_target_market_risk,
    check_target_market_confidence,
    check_target_market_dependency,
    check_target_market_readiness,
    check_standard_family_presence,
    check_standard_family_range,
    check_standard_family_stability,
    check_standard_family_freshness,
    check_standard_family_coverage,
    check_standard_family_consistency,
    check_standard_family_risk,
    check_standard_family_confidence,
    check_standard_family_dependency,
    check_standard_family_readiness,
    check_schema_version_presence,
    check_schema_version_range,
    check_schema_version_stability,
    check_schema_version_freshness,
    check_schema_version_coverage,
    check_schema_version_consistency,
    check_schema_version_risk,
    check_schema_version_confidence,
    check_schema_version_dependency,
    check_schema_version_readiness,
    check_unit_system_presence,
    check_unit_system_range,
    check_unit_system_stability,
    check_unit_system_freshness,
    check_unit_system_coverage,
    check_unit_system_consistency,
    check_unit_system_risk,
    check_unit_system_confidence,
    check_unit_system_dependency,
    check_unit_system_readiness,
    check_language_pack_presence,
    check_language_pack_range,
    check_language_pack_stability,
    check_language_pack_freshness,
    check_language_pack_coverage,
    check_language_pack_consistency,
    check_language_pack_risk,
    check_language_pack_confidence,
    check_language_pack_dependency,
    check_language_pack_readiness,
    check_privacy_tier_presence,
    check_privacy_tier_range,
    check_privacy_tier_stability,
    check_privacy_tier_freshness,
    check_privacy_tier_coverage,
    check_privacy_tier_consistency,
    check_privacy_tier_risk,
    check_privacy_tier_confidence,
    check_privacy_tier_dependency,
    check_privacy_tier_readiness,
    check_safety_threshold_presence,
    check_safety_threshold_range,
    check_safety_threshold_stability,
    check_safety_threshold_freshness,
    check_safety_threshold_coverage,
    check_safety_threshold_consistency,
    check_safety_threshold_risk,
    check_safety_threshold_confidence,
    check_safety_threshold_dependency,
    check_safety_threshold_readiness,
    check_evidence_items_presence,
    check_evidence_items_range,
    check_evidence_items_stability,
    check_evidence_items_freshness,
    check_evidence_items_coverage,
    check_evidence_items_consistency,
    check_evidence_items_risk,
    check_evidence_items_confidence,
    check_evidence_items_dependency,
    check_evidence_items_readiness,
    check_unmapped_fields_presence,
    check_unmapped_fields_range,
    check_unmapped_fields_stability,
    check_unmapped_fields_freshness,
    check_unmapped_fields_coverage,
    check_unmapped_fields_consistency,
    check_unmapped_fields_risk,
    check_unmapped_fields_confidence,
    check_unmapped_fields_dependency,
    check_unmapped_fields_readiness,
    check_waiver_count_presence,
    check_waiver_count_range,
    check_waiver_count_stability,
    check_waiver_count_freshness,
    check_waiver_count_coverage,
    check_waiver_count_consistency,
    check_waiver_count_risk,
    check_waiver_count_confidence,
    check_waiver_count_dependency,
    check_waiver_count_readiness,
    check_test_pass_rate_presence,
    check_test_pass_rate_range,
    check_test_pass_rate_stability,
    check_test_pass_rate_freshness,
    check_test_pass_rate_coverage,
    check_test_pass_rate_consistency,
    check_test_pass_rate_risk,
    check_test_pass_rate_confidence,
    check_test_pass_rate_dependency,
    check_test_pass_rate_readiness,
    check_local_partner_presence,
    check_local_partner_range,
    check_local_partner_stability,
    check_local_partner_freshness,
    check_local_partner_coverage,
    check_local_partner_consistency,
    check_local_partner_risk,
    check_local_partner_confidence,
    check_local_partner_dependency,
    check_local_partner_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
