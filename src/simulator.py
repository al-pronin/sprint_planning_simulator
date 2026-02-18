from typing import List
from src.employee import Employee
from src.feature import Feature


class SprintSimulator:
    def __init__(self, employees: List[Employee], features: List[Feature]):
        self.employees = employees
        self.features = features
        self.day = 0

    def run(self, max_days: int) -> None:
        """Запустить симуляцию на указанное максимальное количество дней."""
        for day in range(1, max_days + 1):
            self.day = day
            print(f"Day {day}")
            self._process_day()
            if not self.features:
                print("All features done!")
                break
            print("------------------")
        else:
            print("Max days reached, simulation stopped.")

    def _process_day(self) -> None:
        # Фаза 1: каждый сотрудник выбирает и выполняет работу (только одну фичу)
        for employee in self.employees:
            self._assign_work(employee)

        # Фаза 2: обработка завершённых стадий и переходы
        self._complete_stages()

        # Подготовка к следующему дню: сброс флага worked_today у всех фич
        for feature in self.features:
            feature.reset_worked_today()

    def _assign_work(self, employee: Employee) -> None:
        """Выбрать для сотрудника подходящую фичу (в порядке приоритета) и назначить работу."""
        for feature in self.features:
            if feature.can_work(employee):
                employee.work_on_feature(feature)
                return
        # Если ничего не подошло
        employee.idle()

    def _complete_stages(self) -> None:
        """Проверить завершённые стадии и выполнить переходы (или удалить готовые фичи)."""
        features_to_remove = []
        for feature in self.features:
            if feature.is_current_stage_finished():
                print(f"{feature.name}: stage {feature.current_stage.name} finished.")
                if not feature.advance_to_next_stage():
                    # Нет следующей стадии — фича полностью готова
                    print(f"Feature `{feature.name}` is done!")
                    features_to_remove.append(feature)
                else:
                    print(f"{feature.name} moved to stage {feature.current_stage.name}.")
                # Важно: НЕ сбрасываем worked_today здесь, чтобы сегодня никто не начал новую стадию

        # Удаляем готовые фичи
        for feature in features_to_remove:
            self.features.remove(feature)