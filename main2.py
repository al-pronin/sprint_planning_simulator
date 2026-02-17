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
    for day_number in range(1, 15):
        print(f'Day {day_number}')
        if not FEATURES:
            print('All done!')
            break
        for employee in EMPLOYEES:
                for feature in FEATURES:
                    if employee in feature.assignees:
                        if feature.current_stage in employee.effective_stages:
                            finished = employee.work(feature)
                            if finished:
                                FEATURES.remove(feature)
                        else:
                            employee.idle()

        print('------------------')
