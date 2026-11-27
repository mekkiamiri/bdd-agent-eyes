# Proposal (English)

**Format**: Tools-in-Action (30 min). Also available as a Quickie (20 min), see the notes.
**Track**: Development practices / testing and quality (rather than the AI track)
**Level**: Intermediate

## Title

The screen changes: my step definitions break, the agent doesn't

## Abstract

When the UI changes but the behaviour doesn't, the step definitions are what breaks: the Gherkin still reads fine, but the glue behind it was looking for a reworded label or a renamed test attribute, while the app still works.

Live, an agent reads each scenario, looks at the screen (screenshot and accessibility tree), clicks, and returns pass, fail or refuse, with no step definitions. On my own small demo app, with 17 scenarios (some deliberately wrong or ambiguous), it gave 204 correct verdicts in 204 runs, refused every ambiguous one with a reason, and survived a UI redesign that broke 7 of 17 Cucumber scenarios. It also costs 14 s and 6 to 9 cents per scenario, against 1.4 s for Cucumber.

You leave with: where to put it (Cucumber in CI; the agent to review scenarios, play a screen that has no glue yet, hold during a redesign); three rules for Gherkin an agent can play; a public repo with the app, the scenarios and the raw results, to rerun the measurement yourself.

## Notes for the committee

- **Everything shown is measured, and in the repo**: github.com/mekkiamiri/bdd-agent-eyes. 17 Gherkin scenarios on a small demo app (11 correct, 3 wrong, 3 ambiguous, ground truth tagged on each). Agent: 153 runs on the original app (3 ways of seeing the screen × 3 runs), 153 correct verdicts, 0 false positives; 51 runs on the redesigned app, 51 correct. Cucumber + Playwright reference in CI: 17/17 on the original app, 10/17 after the redesign (7 correct scenarios broken by two locator changes; and 3 of the 10 that still match only because the trap scenarios now fail on an earlier step). Durations and costs per scenario are in the raw results. Measured on 24-25 November 2026; the bench lets anyone rerun it with today's model.
- **Two live demos, with a plan B**: the agent plays one scenario live (about 20 s); then the redesign, shown as a side-by-side table from the CI run and the agent results. A recorded video of both is ready in case the network or the model fails.
- **Limits said on stage**: the app and the redesign were written by the speaker; one model (Sonnet 5.5); the agent ran on WebKit, Cucumber on Chromium; the step definitions already use roles and labels, so CSS or XPath selectors would likely break more (not measured).
- **Quickie (20 min) variant**: 9 of the 13 slides, the first live demo is dropped, the redesign demo and the results stay.
- **Not a product pitch**: the takeaway is where an agent pays off and where Cucumber stays better (speed, cost, determinism in CI).

## Bio

Mekki is a Tech Lead and system architect, and the AI referent of a software development center. He has practised software craftsmanship for 18 years, with DDD, TDD and BDD at the heart of his work. He has proposed contributions (open pull requests) to Google ADK Java, Spring AI A2A and AG-UI. He likes talks where every number on a slide can be checked in a public repo.
