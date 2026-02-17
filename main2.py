from src.employee import Developer, SystemAnalyst
from src.feature import Feature, FeatureStage

# team
igor = Developer(name ='Igor')

daniil = SystemAnalyst(name ='Daniil')

# features
bepaid_integration = Feature(
    name = 'Bepaid Integration',
    capacity_mapping = {
        FeatureStage.ANALYTICS: 3,
        FeatureStage.DEVELOPMENT: 3,
    },
    current_stage = FeatureStage.ANALYTICS,
)

# planning
bepaid_integration.assign(igor)
bepaid_integration.assign(daniil)

EMPLOYEES = [igor, daniil]
FEATURES = [bepaid_integration]

if __name__ == '__main__':
    for day_number in range(14):
        print(f'Day {day_number}')
        for employee in EMPLOYEES:
            for feature in FEATURES:
                if employee in feature.assignees:
                    if feature.current_stage in employee.effective_stages:
                        employee.work(feature)
                    else:
                        employee.idle()
