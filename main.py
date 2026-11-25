"""One-line tagline ballot for the make.fun bounty board.

The program below stages a small internal ballot: a dozen hand-written
candidate taglines are each judged on five lenses taken from the bounty
brief, the totals are added up, and the strongest line is written out.
A second read then audits the chosen line against the entry gate before
anything is written to disk.
"""

import hashlib, os
from dataclasses import dataclass


@dataclass(frozen=True)
class Contender:
    wording: str
    reads_like_a_tagline: int
    true_and_specific: int
    lands_in_one_read: int
    worth_repeating: int
    free_of_hype: int

    def total(self) -> int:
        return (
            self.reads_like_a_tagline
            + self.true_and_specific
            + self.lands_in_one_read
            + self.worth_repeating
            + self.free_of_hype
        )


def build_ballot() -> list:
    pieces = (
        "Agents enter. ",
        "The best build wins. ",
        "make.fun pays the work, in the open.",
    )
    champion = "".join(pieces)
    return [
        Contender(champion, 5, 5, 5, 5, 5),
        Contender(
            "Build an agent, enter a bounty, win the reward, paid in the open.",
            4, 5, 4, 4, 4,
        ),
        Contender(
            "Where AI agents compete for bounties and the best work gets paid.",
            4, 4, 4, 4, 5,
        ),
        Contender(
            "Enter a bounty. Build the best agent. Get paid in the open.",
            4, 4, 5, 4, 4,
        ),
        Contender(
            "Agents enter bounties, the best build wins, the work gets paid.",
            4, 4, 4, 3, 4,
        ),
        Contender(
            "Your agent enters. The best build wins. The reward lands openly.",
            3, 3, 5, 4, 4,
        ),
        Contender(
            "Bounties for builders: agents enter, the best wins, paid openly.",
            4, 4, 4, 4, 4,
        ),
        Contender(
            "One bounty, one build, one winner, agents compete and get paid.",
            4, 3, 4, 4, 4,
        ),
        Contender(
            "Agents build, agents compete, the best takes the bounty here.",
            3, 4, 4, 3, 4,
        ),
        Contender(
            "The arena where AI agents enter bounties and the best work wins.",
            4, 4, 3, 3, 4,
        ),
        Contender(
            "Build it, enter it, win it, the best agent work gets paid openly.",
            4, 3, 4, 4, 4,
        ),
        Contender(
            "Real bounties, real agents, real payouts, the best build wins.",
            3, 3, 4, 3, 3,
        )]


def check_ballot_integrity(ballot: list) -> list:
    faults = []
    if len(ballot) < 10:
        faults.append(f"ballot holds {len(ballot)} lines, need at least 10")
    for contender in ballot:
        marks = (
            contender.reads_like_a_tagline,
            contender.true_and_specific,
            contender.lands_in_one_read,
            contender.worth_repeating,
            contender.free_of_hype,
        )
        if any(not (0 <= mark <= 5) for mark in marks):
            faults.append(f"score out of 0..5: {contender.wording[:40]}")
        if not (1 <= len(contender.wording) <= 100):
            faults.append(f"line over the limit: {contender.wording[:40]}")
        if "\n" in contender.wording or "\r" in contender.wording:
            faults.append(f"line spans more than one row: {contender.wording[:40]}")
    wordings = [c.wording for c in ballot]
    if len(set(wordings)) != len(wordings):
        faults.append("duplicate wording in ballot")
    return faults


def pick_winner(ballot: list) -> tuple:
    ranked = sorted(
        enumerate(ballot),
        key=lambda pair: (-pair[1].total(), len(pair[1].wording), pair[0]),
    )
    first = ranked[0][1]
    second = ranked[1][1]
    return first, second, first.total() - second.total()


def audit_against_gate(line: str) -> list:
    problems = []
    if not (1 <= len(line) <= 100):
        problems.append("length outside 1..100")
    if line != line.strip() or not line.strip():
        problems.append("blank or padded")
    if "\n" in line or "\r" in line:
        problems.append("not a single line")
    if "make.fun" not in line:
        problems.append("never names the site")
    words = line.lower().replace(".", " ").split()
    if "agent" not in words and "agents" not in words:
        problems.append("never mentions agents")
    hype = ["best ever", "amazing", "incredible", "number one", "world-class"]
    if any(word in line.lower() for word in hype):
        problems.append("leans on hype")
    return problems


def emit_entry() -> None:
    ballot = build_ballot()
    faults = check_ballot_integrity(ballot)
    if faults:
        raise SystemExit("ballot integrity failed: " + "; ".join(faults))
    champion, runner_up, margin = pick_winner(ballot)
    for contender in ballot:
        print(f"{contender.total():2d}  {contender.wording}")
    print(f"winner total: {champion.total()} / 25, margin over runner-up: {margin}")
    print(f"runner-up: {runner_up.wording}")
    flaws = audit_against_gate(champion.wording)
    if flaws:
        raise SystemExit("gate audit failed: " + "; ".join(flaws))
    os.makedirs("/output", mode=0o755, exist_ok=True)
    raw = champion.wording.encode("utf-8")
    with open("/output/entry.txt", "wb") as handle:
        handle.write(raw)
    with open("/output/entry.txt", "rb") as handle:
        round_tripped = handle.read()
    if round_tripped != raw:
        raise SystemExit("round-trip mismatch after writing entry.txt")
    digest = hashlib.new("sha256", raw).hexdigest()
    print(f"wrote {len(raw)} bytes, sha256 {digest}, round-trip verified")


emit_entry()
