from src.employee import Developer, SystemAnalyst, QA
from src.feature import Feature, FeatureStage
from src.simulator import SprintSimulator
from src.strategy import SimpleAssignmentStrategy
from src.reporter import HTMLReporter  # Import the reporter


def main() -> None:
    """Entry point of the sprint simulation 🚀"""

    # 👥 Team
    igor = Developer(name="Igor", productivity_per_day=1.2)
    andrey = Developer(name="Andrey", productivity_per_day=1.2)
    daniil = SystemAnalyst(name="Daniil", productivity_per_day=0.8)
    roman = QA(name="Roman", productivity_per_day=1.0)

    # 📦 Features
    bepaid_integration = Feature(
        name="BePaid Integration",
        stage_capacities={
            FeatureStage.ANALYTICS: 5,
            FeatureStage.DEVELOPMENT: 3,
            FeatureStage.TESTING: 3,
        },
        initial_stage=FeatureStage.ANALYTICS,
    )

    bank131_integration = Feature(
        name="Bank 131 Integration",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 3,
            FeatureStage.TESTING: 3,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )

    withdraw_try = Feature(
        name="Withdraw Try Exchange Info",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 4,
            FeatureStage.TESTING: 2,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )

    # 🎯 Assign people
    for feature in [bepaid_integration, bank131_integration, withdraw_try]:
        feature.assign(roman)

    bepaid_integration.assign(daniil)
    bepaid_integration.assign(igor)
    withdraw_try.assign(igor)

    bank131_integration.assign(andrey)

    simulator = SprintSimulator(
        employees=[igor, daniil, roman, andrey],
        features=[bepaid_integration, bank131_integration, withdraw_try],
        assignment_strategy=SimpleAssignmentStrategy(),
    )

    simulator.run(max_days=15)

    # 🖨️ Generate Report
    reporter = HTMLReporter(simulator.history)
    reporter.save_report("sprint_report.html")


if __name__ == "__main__":
    main()