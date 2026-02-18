from typing import TYPE_CHECKING

from src.employee import Developer, SystemAnalyst, QA
from src.feature import Feature, FeatureStage


if TYPE_CHECKING:
    from src.employee import Employee


# team
igor = Developer(name ='Igor')
daniil = SystemAnalyst(name ='Daniil')
roman = QA(name ='Roman')

# features
bepaid_integration = Feature(
    name = 'BePaid Integration',
    capacity_mapping = {
        FeatureStage.ANALYTICS: 5,
        FeatureStage.DEVELOPMENT: 3,
        FeatureStage.TESTING: 3,
    },
    current_stage = FeatureStage.ANALYTICS,
)

bank131_integration = Feature(
    name = 'Bank 131 Integration',
    capacity_mapping = {
        # FeatureStage.ANALYTICS: 3,
        FeatureStage.DEVELOPMENT: 3,
        FeatureStage.TESTING: 3,
    },
    current_stage = FeatureStage.DEVELOPMENT,
)

# planning
bepaid_integration.assign(igor)
bepaid_integration.assign(daniil)
bepaid_integration.assign(roman)

bank131_integration.assign(igor)
bank131_integration.assign(daniil)
bank131_integration.assign(roman)

EMPLOYEES = [igor, daniil, roman]
FEATURES = [bepaid_integration, bank131_integration]

def calc_employee_day(employee: 'Employee') -> None:
    for feature in FEATURES:
        if employee in feature.assignees:
            if feature.current_stage in employee.effective_stages:
                employee.work(feature)

                if feature.capacity_mapping[feature.current_stage] == 0:
                    feature.capacity_mapping.pop(feature.current_stage)
                    print(f'{employee.name} finished `{feature.name}` {feature.current_stage.name}')

                    remain_stages = list(feature.capacity_mapping.keys())
                    if len(remain_stages) == 0:
                        print(f'Feature `{feature.name}` is done!')
                        FEATURES.remove(feature)
                    else:
                        feature.current_stage = list(feature.capacity_mapping.keys())[0]
                return


            # else:
            #     print(f'{employee.name} cant\'t work on `{feature.name}`')
    employee.idle()



if __name__ == '__main__':
    for day_number in range(1, 15):
        print(f'Day {day_number}')
        for employee in EMPLOYEES:
            calc_employee_day(employee)
        if not FEATURES:
            print('All done!\n------------------')
            break
        print('------------------')
