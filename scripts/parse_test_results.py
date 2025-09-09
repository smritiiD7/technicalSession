import xml.etree.ElementTree as ET

tree = ET.parse("report.xml")
root = tree.getroot()

total = failures = errors = skipped = 0

# Sum attributes from all <testsuite> elements
for ts in root.findall("testsuite"):
    total += int(ts.attrib.get("tests", 0))
    failures += int(ts.attrib.get("failures", 0))
    errors += int(ts.attrib.get("errors", 0))
    skipped += int(ts.attrib.get("skipped", 0))

passed = total - failures - errors - skipped

summary = (
    f"🧪 *Test Report by Ashish*:\n"
    f"✅ Passed: {passed}\n"
    f"❌ Failed: {failures + errors}\n"
    f"⚠️ Skipped: {skipped}\n"
    f"📊 Total: {total}"
)

with open("slack_msg.txt", "w") as f:
    f.write(summary)
