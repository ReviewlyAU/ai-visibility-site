#!/usr/bin/env python3
"""
check_claims.py: stop unsupported claims about Reviewly reaching the live site.

Copied from geooptimisation-site (added there 4 Nov 2026 after AI-written pages went live saying Reviewly was the "only
Australian agency", got "first-page rankings within days", and quoted made-up
client results (340%, 312%, 173%, 4.4x)). This copy adds rules for
ai-visibility.com.au: no (R) mark, em dashes, retired names or unapproved percentages.

Runs in GitHub Actions before every deploy (deploy.yml) and every pull request
preview (preview.yml). If it fails, nothing is uploaded.

Run by hand:  python check_claims.py            (checks every .html file)
              python check_claims.py a.html b.html

Figures with a Proof Register entry (Brand Bible R17): a number is allowed when
the exact sentence it sits in is listed in proof-register-figures.txt with its Proof Register
ID (format: "PR-018 | exact sentence as it appears on the page"). Add a line only
after Tanya has signed off that entry, in a reviewed pull request. The entry only
lifts the figure rules (percentages, client results, multipliers); guarantees,
exclusivity, retired names and the rest still apply to that sentence.

To allow any other phrase that is genuinely supported, change the pattern here in
a reviewed pull request. Do not switch the check off.
"""
import html
import pathlib
import re
import sys

PCT = r"\d{1,4}(\.\d+)?\s?(%|per\s?cent)"
FIGURES_FILE = "proof-register-figures.txt"

# (pattern, why it is banned). Matched case-insensitively against page text with tags removed.
BANNED = [
    (r"\bonly\s+(australian\s+)?(agency|firm|company|partner|provider)\b",
     "'only ... agency' style exclusivity claim"),
    (r"\b(exclusively|only)\s+(by|through|from|with)\s+reviewly\b|\bnot\s+available\s+(through|from)\s+any\s+other\b",
     "exclusivity claim"),
    (r"\b(first|1st)[- ]page\s+rankings?\b",
     "promise of first-page rankings"),
    (r"\bwithin\s+(a\s+few|\d+|one|two|three|four|five|six|seven|ten|fourteen|thirty)\s+days?\b",
     "results-within-days promise"),
    (r"\breviewly\b[^.]{0,60}?(#\s?1|\bnumber\s+one|\bno\.\s?1|\bleading\b|\bbest\b)|(#\s?1|\bnumber\s+one)\s+(within|agency|partner|provider)\b",
     "'#1 / best' ranking claim about Reviewly"),
    (r"\bnine\s+times\b|\b\d+(\.\d+)?\s?x\s+(valuation|more|increase|growth|return|roi)\b",
     "multiplier result claim"),
    (r"\b(client|customer|provider|business|practice|firm)s?\b[^.]{0,120}?\b(improved|increased|grew|lifted|achieved|saw)\b[^.]{0,80}?" + PCT,
     "client result quoted as a percentage"),
    (PCT + r"[^.]{0,80}?\b(after|since)\s+(working\s+with|implementing|engaging)\b",
     "before-and-after result percentage"),
    (r"\bcase\s+study\s*(snapshot|snippet|:)",
     "case study (needs a real client and Tanya's approval)"),
    (r"\bguaranteed?\b[^.]{0,60}?\b(rank|ranking|citation|recommend|results?)",
     "guaranteed outcome"),
    (r"\breviewly('s)?\b[^.]{0,40}?\b(software|platform|review\s+tool|seo\s+agency|saas)\b",
     "Reviewly described as software / platform / SEO agency"),
    # ai-visibility.com.au additions (8 Nov 2026, Brand Bible V7.1)
    (r"®", "(R) mark: the REVIEW Method uses TM, never (R)"),
    (r"—", "em dash: use a comma or colon"),
    (r"\bsatellite\s+search\b|\bturbo\s+subdomains\b|\bproject\s+frontier\b",
     "retired name"),
    (PCT, "percentage figure: needs an approved Proof Register entry (R17) before it goes on a page"),
]
# Rules that a listed Proof Register sentence is allowed to pass.
FIGURE_RULES = {
    "multiplier result claim",
    "client result quoted as a percentage",
    "before-and-after result percentage",
    "percentage figure: needs an approved Proof Register entry (R17) before it goes on a page",
}
COMPILED = [(re.compile(p, re.I), why) for p, why in BANNED]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def load_figures(root: pathlib.Path) -> list:
    """Exact sentences listed in the figures file. A malformed line stops the check."""
    f = root / FIGURES_FILE
    if not f.exists():
        return []
    out = []
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"\s*(PR-\d{3,})\s*\|\s*(.+)$", line)
        if not m:
            raise SystemExit(f"{FIGURES_FILE} line {n}: expected 'PR-000 | exact sentence'")
        out.append((m.group(1), norm(m.group(2))))
    return out

TAG_RE = re.compile(r"<[^>]+>")
# Block-level tags become sentence breaks so a match cannot run across separate page elements.
BLOCK_RE = re.compile(r"</?(p|div|li|ul|ol|h[1-6]|tr|td|th|section|article|br|table|button)\b[^>]*>", re.I)
CHROME_RE = re.compile(r"<(nav|header|footer)\b.*?</\1>", re.S | re.I)


def page_text(content: str) -> str:
    """Visible body text plus JSON-LD (FAQ schema answers are read by AI engines too)."""
    text = re.sub(r"<style\b.*?</style>", " ", content, flags=re.S | re.I)
    text = re.sub(r"<script\b(?![^>]*ld\+json).*?</script>", " ", text, flags=re.S | re.I)
    text = CHROME_RE.sub(" . ", text)
    text = BLOCK_RE.sub(" . ", text)
    text = TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", html.unescape(text))


def find_problems(content: str, figures: list = ()) -> list:
    text = page_text(content)
    spans = []
    for _pid, sentence in figures:
        for m in re.finditer(re.escape(sentence), text):
            spans.append((m.start(), m.end()))
    problems = []
    for rx, why in COMPILED:
        for m in rx.finditer(text):
            if why in FIGURE_RULES and any(a <= m.start() and m.end() <= b for a, b in spans):
                continue
            start = max(0, m.start() - 50)
            snippet = text[start:m.end() + 30].strip()
            problems.append(f'{why}: "...{snippet}..."')
    return problems


def main(argv: list) -> int:
    root = pathlib.Path(__file__).parent
    files = [pathlib.Path(a) for a in argv] or sorted(
        p for p in root.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts
    )
    figures = load_figures(root)
    failed = 0
    for f in files:
        problems = find_problems(f.read_text(encoding="utf-8", errors="replace"), figures)
        if problems:
            failed += 1
            print(f"\n{f}:")
            for p in problems:
                print(f"  - {p}")
    if failed:
        print(f"\nClaims check FAILED on {failed} file(s). Remove or rewrite these before merging.")
        return 1
    print(f"Claims check passed ({len(files)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
