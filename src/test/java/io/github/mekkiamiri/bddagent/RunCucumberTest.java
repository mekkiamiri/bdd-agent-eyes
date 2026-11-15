package io.github.mekkiamiri.bddagent;

import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectDirectories;
import org.junit.platform.suite.api.Suite;

/** Joue les scénarios de features/ (à la racine du dépôt) avec le moteur Cucumber. */
@Suite
@IncludeEngines("cucumber")
@SelectDirectories("features")
public class RunCucumberTest {
}
