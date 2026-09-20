class ContentError(Exception):
    """Raised with every problem found in content/, not just the first."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        body = "\n".join(f"  - {p}" for p in problems)
        super().__init__(f"{len(problems)} problem(s) in content/:\n{body}")
