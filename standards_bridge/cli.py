from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from standards_bridge.verification_hub import Application, run, verify
from standards_bridge.profiles.specification import ContractError


def _load_json_argument(value: str) -> dict:
    if value.startswith("@"):
        text = Path(value[1:]).read_text(encoding="utf-8")
    else:
        path = Path(value)
        text = path.read_text(encoding="utf-8") if path.is_file() else value
    body = json.loads(text)
    if not isinstance(body, dict):
        raise ContractError("JSON argument must be an object")
    return body


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='standards_bridge', description='中国—东盟人工智能标准适配验证台')
    commands = root.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    check = commands.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--database", required=True)

    compare = commands.add_parser("compare", help="layer one cross-market case pair")
    compare.add_argument("--database", required=True)
    compare.add_argument("--left", required=True)
    compare.add_argument("--right", required=True)

    comparability = commands.add_parser("comparability", help="stratified pass rates and reuse eligibility")
    comparability.add_argument("--database", required=True)

    mapping = commands.add_parser("mapping", help="register or inspect a standard mapping")
    mapping_sub = mapping.add_subparsers(dest="mapping_command", required=True)
    register = mapping_sub.add_parser("register")
    register.add_argument("--database", required=True)
    register.add_argument("--mapping-id", required=True)
    register.add_argument("--source", required=True)
    register.add_argument("--target", required=True)
    register.add_argument("--aliases", required=True, help="JSON object or @path-to-json")
    impact = mapping_sub.add_parser("impact")
    impact.add_argument("--database", required=True)
    impact.add_argument("--mapping-id", required=True)

    link = commands.add_parser("link-case")
    link.add_argument("--database", required=True)
    link.add_argument("--case-id", required=True)
    link.add_argument("--mapping-id", required=True)

    sign = commands.add_parser("sign-case")
    sign.add_argument("--database", required=True)
    sign.add_argument("--certification-id", required=True)
    sign.add_argument("--case-id", required=True)
    sign.add_argument("--mapping-id", required=True)
    sign.add_argument("--evidence", required=True, help="JSON object or @path-to-json")

    revision = commands.add_parser("revision", help="revision impact and revalidation status")
    revision.add_argument("--database", required=True)
    revision.add_argument("--mapping-id", required=True)

    revalidate = commands.add_parser("revalidate", help="submit a revalidation result for one case")
    revalidate.add_argument("--database", required=True)
    revalidate.add_argument("--mapping-id", required=True)
    revalidate.add_argument("--case-id", required=True)
    revalidate.add_argument("--result", required=True, help="JSON object or @path-to-json")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "run":
        result = run(args.fixture, args.database, args.output)
    elif args.command == "verify":
        result = verify(args.database, args.output)
    elif args.command == "inspect":
        result = Application(args.database).inspect()
    elif args.command == "compare":
        result = Application(args.database).compare_cases(args.left, args.right)
    elif args.command == "comparability":
        result = Application(args.database).comparability_view()
    elif args.command == "revision":
        result = Application(args.database).revision_view(args.mapping_id)
    elif args.command == "revalidate":
        result = Application(args.database).revalidate_case(
            args.mapping_id, args.case_id, _load_json_argument(args.result))
    elif args.command == "link-case":
        application = Application(args.database)
        application.repository.link_case_mapping(args.case_id, args.mapping_id)
        result = {"linked": {"case_id": args.case_id, "mapping_id": args.mapping_id}}
    elif args.command == "sign-case":
        application = Application(args.database)
        result = application.repository.sign_case(
            args.certification_id, args.case_id, args.mapping_id,
            _load_json_argument(args.evidence))
    elif args.command == "mapping":
        application = Application(args.database)
        if args.mapping_command == "register":
            aliases = _load_json_argument(args.aliases)
            revision = application.register_mapping(args.mapping_id, args.source, args.target, aliases)
            result = {"mapping_id": args.mapping_id, "revision": revision}
        else:
            result = application.mapping_impact(args.mapping_id)
    else:  # pragma: no cover - argparse rejects unknown commands
        result = {}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
