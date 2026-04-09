#!/usr/bin/env python3
"""Quick test to check if LocalizedNames and Descriptions are being parsed."""

import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent.parent.parent / "ui-tools" / "scripts"
sys.path.insert(0, str(scripts_dir))

from formxml_parser import FormXmlParser

# Test with Capture 03 (Sample baseline)
capture03_path = Path(__file__).resolve().parent.parent / "captures" / "03 - Sample Table" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main" / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"

print("Parsing Capture 03 (Sample baseline)...")
form = FormXmlParser.parse_file(capture03_path)

print(f"Form ID: {form.formid}")
print(f"Form name: {form.form_name}")
print(f"\nLocalized_names: {len(form.localized_names)} items")
for ln in form.localized_names:
    print(f"  - {ln.description} (lang: {ln.languagecode})")

print(f"\nDescriptions: {len(form.descriptions)} items")
for desc in form.descriptions:
    print(f"  - {desc.description} (lang: {desc.languagecode})")

# Now write it back and check
output_path = Path(__file__).resolve().parent / "roundtrip_test.xml"
FormXmlParser.write_file(form, output_path)
print(f"\nWrote to: {output_path}")
print("Check if LocalizedNames and Descriptions are in the output!")
