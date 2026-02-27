"""
Main entry point for the sprint simulation.

This script demonstrates the full simulation workflow including:
- Team configuration
- Feature setup with code review
- Simulation execution
- HTML report generation
"""

from src.employee import Developer, QA, SystemAnalyst
from src.feature import Feature, FeatureStage
from src.reporter import HTMLReporter
from src.simulator import SprintSimulator
from src.strategy import SimpleAssignmentStrategy


def main() -> None:
    """
    Entry point of the sprint simulation.

    This function demonstrates how to set up and run a sprint simulation
    with multiple features and team members, including the code review mechanic.

    Code Review Rules:
    - CODE_REVIEW stage is auto-added after DEVELOPMENT (20% of dev effort)
    - Any Developer in the team can review
    - Reviewers must NOT have contributed to development
    - If all developers are assigned to feature development, validation fails
    """
    # ------------------------------------------------------------------ #
    # 👥 Team Configuration
    # ------------------------------------------------------------------ #

    # Developers - can work on DEVELOPMENT and CODE_REVIEW stages
    igor = Developer(name="Igor", productivity_per_day=1.2)
    andrey = Developer(name="Andrey", productivity_per_day=1.2)

    # Analyst - works on ANALYTICS stage only
    daniil = SystemAnalyst(name="Daniil", productivity_per_day=0.8)

    # QA - works on TESTING stage only
    roman = QA(name="Roman", productivity_per_day=1.0)

    # ------------------------------------------------------------------ #
    # 📦 Features
    # ------------------------------------------------------------------ #

    # Feature with full pipeline: Analytics → Development → Code Review → Testing
    # Code Review is auto-added with 20% of development effort = 0.6h
    bepaid_integration = Feature(
        name="BePaid Integration",
        stage_capacities={
            FeatureStage.ANALYTICS: 5.0,
            FeatureStage.DEVELOPMENT: 3.0,
            FeatureStage.TESTING: 3.0,
        },
        initial_stage=FeatureStage.ANALYTICS,
    )

    # Feature starting at development stage
    # Code Review auto-added: 0.6h
    bank131_integration = Feature(
        name="Bank 131 Integration",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 3.0,
            FeatureStage.TESTING: 3.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )

    # Another feature starting at development
    # Code Review auto-added: 0.8h
    withdraw_try = Feature(
        name="Withdraw Try Exchange Info",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 4.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )

    # ------------------------------------------------------------------ #
    # 🎯 Assignments (Important for Code Review!)
    # ------------------------------------------------------------------ #
    # Key principle: External reviewers are Developers NOT assigned to the feature.
    # They will be available to do CODE_REVIEW because they didn't contribute.

    # QA is assigned to all features for testing
    for feature in [bepaid_integration, bank131_integration, withdraw_try]:
        feature.assign(roman)

    # Analyst assigned to BePaid
    bepaid_integration.assign(daniil)

    # Developer assignments:
    # - Igor works on BePaid and Withdraw
    # - Andrey works on Bank 131
    # - IMPORTANT: Each feature needs at least one developer NOT assigned
    #   to it, who can serve as external reviewer.

    bepaid_integration.assign(igor)
    withdraw_try.assign(igor)
    bank131_integration.assign(andrey)

    # Code Review Coverage:
    # - BePaid: Igor contributed → Andrey can review (not assigned to BePaid)
    # - Bank 131: Andrey contributed → Igor can review (not assigned to Bank 131)
    # - Withdraw: Igor contributed → Andrey can review (not assigned to Withdraw)

    # ------------------------------------------------------------------ #
    # 🚀 Run Simulation
    # ------------------------------------------------------------------ #

    simulator = SprintSimulator(
        employees=[igor, daniil, roman, andrey],
        features=[bepaid_integration, bank131_integration, withdraw_try],
        assignment_strategy=SimpleAssignmentStrategy(),
    )

    simulator.run(max_days=15)

    # ------------------------------------------------------------------ #
    # 🖨️ Generate Report
    # ------------------------------------------------------------------ #

    reporter = HTMLReporter(simulator.history)
    reporter.save_report("sprint_report.html")


if __name__ == "__main__":
    main()
