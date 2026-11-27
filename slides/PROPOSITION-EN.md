# Proposal (English)

**Format**: Tools-in-Action (30 min). Also available as a Quickie (20 min), see the notes.
**Track**: Development practices
**Level**: Intermediate

## Title

Your Gherkin, played by an agent that sees the screen

## Abstract

Step definitions are the most fragile code in a BDD project: the Gherkin reads fine, but the glue behind it breaks on a renamed label or a moved button, while the app still works.

Live, an agent reads each scenario, looks at the screen (screenshot and accessibility tree), clicks, and returns pass, fail or refuse, with no step definitions. On 17 trapped scenarios it gave 204 correct verdicts out of 204, refused every ambiguous one with a reason, and survived a UI redesign that broke 7 of 17 Cucumber scenarios. It also costs 14 s and 6 to 9 cents per scenario, against 1.4 s for Cucumber.

You leave with where to put it (Cucumber in CI; the agent to review scenarios, explore a new screen, cover a redesign), three rules for Gherkin an agent can play, and a public repo with the app, the scenarios and the raw results.

## Notes for the committee

- **Everything shown is measured, and in the repo**: github.com/mekkiamiri/bdd-agent-eyes. 17 Gherkin scenarios on a small demo app (11 correct, 3 wrong, 3 ambiguous, ground truth tagged on each). Agent: 153 runs on the original app (3 ways of seeing the screen × 3 runs), 153 correct verdicts, 0 false positives; 51 runs on the redesigned app, 51 correct. Cucumber + Playwright reference in CI: 17/17 on the original app, 10/17 after the redesign (7 correct scenarios broken by two locator changes, plus 3 traps that still fail but for the wrong reason). Durations and costs per scenario are in the raw results.
- **Two live demos, with a plan B**: the agent plays one scenario live (about 20 s); then the redesign, shown as a side-by-side table from the CI run and the agent results. A recorded video of both is ready in case the network or the model fails.
- **Limits said on stage**: the app and the redesign were written by the speaker; one model (Sonnet 5.5); the agent ran on WebKit, Cucumber on Chromium; the step definitions already use roles and labels, so CSS or XPath selectors would likely break more (not measured).
- **Quickie (20 min) variant**: 9 of the 14 slides, the first live demo is dropped, the redesign demo and the results stay.
- **Not a product pitch**: the takeaway is where an agent pays off and where Cucumber stays better (speed, cost, determinism in CI).

## Bio

Mekki is a Tech Lead and system architect, and the AI referent of a software development center. He has practised software craftsmanship for 18 years, with DDD, TDD and BDD at the heart of his work. He has proposed contributions (open pull requests) to Google ADK Java, Spring AI A2A and AG-UI. He likes talks where every number on a slide can be checked in a public repo.
