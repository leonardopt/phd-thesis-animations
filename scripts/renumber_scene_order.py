#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import OrderedDict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

STUDY_CONFIG = {
    "study1": {
        "scene_file": REPO_ROOT / "scenes" / "study1.py",
        "order_var": "_STUDY1_SCENE_ORDER",
        "overrides_var": "_STUDY1_OUTPUT_NAME_OVERRIDES",
        "docstring_numbered_classes": True,
    },
    "study2": {
        "scene_file": REPO_ROOT / "scenes" / "study2.py",
        "order_var": "_STUDY2_SCENE_ORDER",
        "overrides_var": None,
        "docstring_numbered_classes": False,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove one numbered scene from a study scene-order mapping and "
            "compact later scene numbers automatically."
        )
    )
    parser.add_argument("study", choices=tuple(STUDY_CONFIG))
    parser.add_argument(
        "--remove-class",
        required=True,
        help="Scene class name to remove from the numbered order, then compact later numbers.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the updated mapping back to the scene file. Default is dry-run.",
    )
    return parser.parse_args()


def load_python_module(path: Path) -> tuple[str, ast.Module]:
    source = path.read_text(encoding="utf-8")
    return source, ast.parse(source)


def load_literal_mapping(
    module: ast.Module,
    variable_name: str,
    source_path: Path,
) -> OrderedDict[str, str]:
    for node in module.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
            value = node.value
        elif isinstance(node, ast.Assign):
            value = node.value
            for candidate in node.targets:
                if isinstance(candidate, ast.Name):
                    target = candidate.id
                    if target == variable_name:
                        break
        else:
            continue

        if target == variable_name:
            literal = ast.literal_eval(value)
            if not isinstance(literal, dict):
                raise SystemExit(f"{variable_name} in {source_path} is not a dict literal.")
            return OrderedDict((str(key), str(val)) for key, val in literal.items())

    raise SystemExit(f"Could not find {variable_name} in {source_path}.")


def find_assignment_span(module: ast.Module, variable_name: str) -> tuple[int, int]:
    for node in module.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == variable_name:
                return node.lineno, node.end_lineno
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    return node.lineno, node.end_lineno
    raise SystemExit(f"Could not find {variable_name} assignment span.")


def parse_number_label(label: str) -> tuple[int, str, int]:
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", label)
    if match is None:
        raise SystemExit(f"Unsupported scene number label: {label!r}")
    digits, suffix = match.groups()
    return int(digits), suffix, len(digits)


def shift_number_label(label: str, removed_base_number: int) -> str:
    base_number, suffix, width = parse_number_label(label)
    if base_number > removed_base_number:
        base_number -= 1
    return f"{base_number:0{width}d}{suffix}"


def build_updated_order(
    order_mapping: OrderedDict[str, str],
    removed_class: str,
) -> tuple[OrderedDict[str, str], str]:
    if removed_class not in order_mapping:
        known = ", ".join(order_mapping.keys())
        raise SystemExit(f"{removed_class} is not in the scene order. Known classes: {known}")

    removed_label = order_mapping[removed_class]
    removed_base_number, _, _ = parse_number_label(removed_label)
    updated = OrderedDict()

    for class_name, label in order_mapping.items():
        if class_name == removed_class:
            continue
        updated[class_name] = shift_number_label(label, removed_base_number)

    return updated, removed_label


def build_updated_overrides(
    overrides: OrderedDict[str, str],
    updated_order: OrderedDict[str, str],
    removed_class: str,
) -> OrderedDict[str, str]:
    updated = OrderedDict()
    for class_name, output_name in overrides.items():
        if class_name == removed_class:
            continue
        if class_name not in updated_order:
            continue

        default_output_name = f"{updated_order[class_name]}_{class_name}"
        if output_name.endswith(f"_{class_name}"):
            updated[class_name] = default_output_name
        else:
            updated[class_name] = output_name
    return updated


def format_mapping_block(variable_name: str, mapping: OrderedDict[str, str]) -> str:
    if not mapping:
        return f"{variable_name}: dict[str, str] = {{}}\n"

    lines = [f"{variable_name}: dict[str, str] = {{\n"]
    for key, value in mapping.items():
        lines.append(f'    "{key}": "{value}",\n')
    lines.append("}\n")
    return "".join(lines)


def replace_line_span(source: str, start_line: int, end_line: int, replacement: str) -> str:
    lines = source.splitlines(keepends=True)
    replacement_lines = replacement.splitlines(keepends=True)
    if replacement_lines and not replacement_lines[-1].endswith("\n"):
        replacement_lines[-1] += "\n"
    lines[start_line - 1 : end_line] = replacement_lines
    return "".join(lines)


def update_numbered_docstring_lines(
    source: str,
    module: ast.Module,
    updated_order: OrderedDict[str, str],
    removed_class: str,
) -> str:
    if not module.body:
        return source
    first_node = module.body[0]
    if not (
        isinstance(first_node, ast.Expr)
        and isinstance(first_node.value, ast.Constant)
        and isinstance(first_node.value.value, str)
    ):
        return source

    lines = source.splitlines(keepends=True)
    start = first_node.lineno - 1
    end = first_node.end_lineno
    doc_lines = lines[start:end]
    pattern = re.compile(r"^(\s*)(\d+[A-Za-z]*)(\s+)([A-Za-z0-9_]+)(\s*)$")
    updated_doc_lines: list[str] = []

    for line in doc_lines:
        match = pattern.match(line.rstrip("\n"))
        if match is None:
            updated_doc_lines.append(line)
            continue

        indent, _old_number, gap, class_name, trailing = match.groups()
        if class_name == removed_class:
            continue
        if class_name not in updated_order:
            updated_doc_lines.append(line)
            continue

        newline = "\n" if line.endswith("\n") else ""
        updated_doc_lines.append(
            f"{indent}{updated_order[class_name]}{gap}{class_name}{trailing}{newline}"
        )

    lines[start:end] = updated_doc_lines
    return "".join(lines)


def print_summary(
    study: str,
    scene_path: Path,
    removed_class: str,
    removed_label: str,
    old_order: OrderedDict[str, str],
    new_order: OrderedDict[str, str],
) -> None:
    print(f"Study: {study}")
    print(f"Scene file: {scene_path}")
    print(f"Removed: {removed_label} {removed_class}")
    print("")
    print("Shifted scene numbers:")
    for class_name, old_label in old_order.items():
        if class_name == removed_class:
            print(f"  - {old_label} {class_name} -> removed")
            continue
        new_label = new_order[class_name]
        if new_label != old_label:
            print(f"  - {old_label} {class_name} -> {new_label}")
    print("")
    print("Follow-up after applying:")
    print(f"  - rerender {study} at the qualities you care about")
    print("  - rebuild any backup PDFs / emergency bundle that depend on those videos")
    print("  - regenerate or delete stale generated reports under media/reports/")


def main() -> int:
    args = parse_args()
    config = STUDY_CONFIG[args.study]
    scene_path: Path = config["scene_file"]
    source, module = load_python_module(scene_path)

    old_order = load_literal_mapping(module, config["order_var"], scene_path)
    new_order, removed_label = build_updated_order(old_order, args.remove_class)

    new_source = replace_line_span(
        source,
        *find_assignment_span(module, config["order_var"]),
        format_mapping_block(config["order_var"], new_order),
    )

    overrides_var = config["overrides_var"]
    if overrides_var is not None:
        updated_module = ast.parse(new_source)
        old_overrides = load_literal_mapping(module, overrides_var, scene_path)
        new_overrides = build_updated_overrides(old_overrides, new_order, args.remove_class)
        new_source = replace_line_span(
            new_source,
            *find_assignment_span(updated_module, overrides_var),
            format_mapping_block(overrides_var, new_overrides),
        )

    if config["docstring_numbered_classes"]:
        new_source = update_numbered_docstring_lines(
            new_source,
            ast.parse(new_source),
            new_order,
            args.remove_class,
        )

    print_summary(
        study=args.study,
        scene_path=scene_path,
        removed_class=args.remove_class,
        removed_label=removed_label,
        old_order=old_order,
        new_order=new_order,
    )

    if not args.apply:
        print("")
        print("Dry-run only. Re-run with --apply to write the updated numbering.")
        return 0

    scene_path.write_text(new_source, encoding="utf-8")
    print("")
    print(f"Wrote updated numbering to {scene_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
