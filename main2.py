# main2.py
from src.employee import Developer, SystemAnalyst, QA
from src.feature import Feature, FeatureStage
from src.simulator import SprintSimulator


if __name__ == '__main__':
    # Команда
    igor = Developer(name='Igor', productivity=1.2)
    daniil = SystemAnalyst(name='Daniil', productivity=0.8)
    roman = QA(name='Roman', productivity=1.0)

    # Фичи
    bepaid_integration = Feature(
        name='BePaid Integration',
        capacity_mapping={
            FeatureStage.ANALYTICS: 5,
            FeatureStage.DEVELOPMENT: 3,
            FeatureStage.TESTING: 3,
        },
        current_stage=FeatureStage.ANALYTICS,
    )

    bank131_integration = Feature(
        name='Bank 131 Integration',
        capacity_mapping={
            FeatureStage.DEVELOPMENT: 3,
            FeatureStage.TESTING: 3,
        },
        current_stage=FeatureStage.DEVELOPMENT,
    )

    withdraw_try = Feature(
        name='withdraw try exchange info',
        capacity_mapping={
            FeatureStage.DEVELOPMENT: 4,
            FeatureStage.TESTING: 2,
        },
        current_stage=FeatureStage.DEVELOPMENT,
    )

    # Назначение сотрудников
    bepaid_integration.assign(igor)
    bepaid_integration.assign(daniil)
    bepaid_integration.assign(roman)

    bank131_integration.assign(igor)
    bank131_integration.assign(roman)

    withdraw_try.assign(igor)
    withdraw_try.assign(roman)

    employees = [igor, daniil, roman]
    features = [bepaid_integration, bank131_integration, withdraw_try]

    sim = SprintSimulator(employees, features)
    sim.run(max_days=15)