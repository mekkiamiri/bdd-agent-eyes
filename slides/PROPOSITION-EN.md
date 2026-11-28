# Proposal (English)

**Format**: Tools-in-Action (30 min). Also available as a Quickie (20 min), see the notes.
**Track**: Development practices / testing and quality (rather than the AI track)
**Level**: Intermediate

## Title

The screen changes: my step definitions break, the agent doesn't

## Abstract

You write Gherkin, and Cucumber plays it through step definitions, the glue code that finds each button. The day the front end redesigns a screen without changing its behaviour, that glue is what breaks: on my demo app, one redesign breaks 7 of 17 scenarios, and 3 more still "match" while testing nothing.

The target: scenarios that survive redesigns, with an explained verdict, without rewriting the glue. Live, gherkin-eyes, an open source tool I built on Playwright MCP, has an agent read each scenario, look at the screen, click, and answer pass, fail or refuse (ambiguous scenario), with a screenshot as evidence. Measured with the same agent: 204 correct verdicts in 204 runs, redesign included; but 28 s and 12 cents per scenario.

You leave with: gherkin-eyes (one command, an HTML report and a JUnit file for CI); three moves: keep Cucumber in CI, run the agent after a redesign or on new scenarios, write Gherkin with three rules.

## Notes for the committee

- **The tool**: gherkin-eyes (outil/ folder, Python standard library only, Apache-2.0): `gherkin-eyes features/ --url <app>` writes an HTML report (verdict, explanation, final screenshot) and a JUnit XML file. Real output in outil/exemple/ (17/17 verdicts matching the ground truth, 2 min 24 s, USD 1.98). Verdicts checked blind: on 10 sampled runs (the 6 trap scenarios and 4 correct ones drawn at random), another model seeing only the scenario and the final screenshot agreed 9 times (the one disagreement is refuse vs fail, never a wrong pass), and the agent's written evidence matched the screen 10 times out of 10.
- **Everything shown is measured, and in the repo**: github.com/mekkiamiri/bdd-agent-eyes. 17 Gherkin scenarios on a small demo app (11 correct, 3 wrong, 3 ambiguous, ground truth tagged on each). Agent: 153 runs on the original app (3 ways of seeing the screen × 3 runs), 153 correct verdicts, 0 false positives; 51 runs on the redesigned app, 51 correct. Cucumber + Playwright reference in CI: 17/17 on the original app, 10/17 after the redesign (7 correct scenarios broken by two locator changes; and 3 of the 10 that still match only because the trap scenarios now fail on an earlier step). Durations and costs per scenario are in the raw results. Measured on 24-25 November 2026; the bench lets anyone rerun it with today's model.
- **Live demo, with a plan B**: gherkin-eyes plays one scenario live (about 20 s) and opens its report; then the same command on the redesigned app. Pre-generated reports (outil/exemple/) and a recorded video are ready in case the network or the model fails.
- **Limits said on stage**: the app and the redesign were written by the speaker; one model (Sonnet 5.5); the agent ran on WebKit, Cucumber on Chromium; the step definitions already use roles and labels, so CSS or XPath selectors would likely break more (not measured).
- **Structure**: starting point (Gherkin + step definitions) → problem (the redesign breaks 7 of 17) → target (verdicts that survive and explain themselves) → how (gherkin-eyes + 3 moves).
- **Quickie (20 min) variant**: 9 of the 13 slides, the tool demo stays.
- **Not a product pitch**: the takeaway is where an agent pays off and where Cucumber stays better (speed, cost, determinism in CI).

## Bio

Mekki is a Tech Lead and system architect, and the AI referent of a software development center. He has practised software craftsmanship for 18 years, with DDD, TDD and BDD at the heart of his work. He has proposed contributions (open pull requests) to Google ADK Java, Spring AI A2A and AG-UI. He likes talks where every number on a slide can be checked in a public repo.
