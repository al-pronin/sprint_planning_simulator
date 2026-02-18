# src/feature.py
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    NEW = 'new'
    ANALYTICS = 'analytics'
    DEVELOPMENT = 'development'
    TESTING = 'testing'


class Feature:
    # Порядок прохождения стадий (можно менять в наследниках)
    stage_order = [FeatureStage.ANALYTICS, FeatureStage.DEVELOPMENT, FeatureStage.TESTING]

    def __init__(
        self,
        name: str,
        capacity_mapping: Dict[FeatureStage, float],
        current_stage: FeatureStage
    ):
        self.name = name
        # Исходное отображение (для справки)
        self.capacity_mapping = capacity_mapping.copy()
        # Оставшаяся трудоёмкость по каждой стадии (может быть дробной)
        self.remaining = capacity_mapping.copy()
        self.current_stage = current_stage
        self.assignees: List['Employee'] = []
        self.worked_today = False  # флаг: работали ли сегодня над этой фичей

    def assign(self, employee: 'Employee') -> None:
        """Назначить сотрудника на фичу."""
        if employee not in self.assignees:
            self.assignees.append(employee)

    def can_work(self, employee: 'Employee') -> bool:
        """Может ли сотрудник работать над фичей сегодня."""
        if self.worked_today:
            return False
        if employee not in self.assignees:
            return False
        if self.current_stage not in employee.effective_stages:
            return False
        # Дополнительно можно проверить, не заблокирована ли фича (для будущих расширений)
        return True

    def work(self, employee: 'Employee') -> None:
        """Выполнить единицу работы над текущей стадией."""
        if self.remaining.get(self.current_stage, 0) <= 0:
            raise RuntimeError(f"Stage {self.current_stage} of feature {self.name} is already finished.")
        self.remaining[self.current_stage] -= employee.productivity
        self.worked_today = True

    def is_current_stage_finished(self) -> bool:
        """Завершена ли текущая стадия (остаток <= 0)."""
        return self.remaining.get(self.current_stage, 0) <= 0

    def advance_to_next_stage(self) -> bool:
        """
        Перейти на следующую стадию согласно порядку.
        Возвращает True, если переход выполнен, и False, если стадий больше нет (фича готова).
        """
        try:
            current_idx = self.stage_order.index(self.current_stage)
        except ValueError:
            # Текущая стадия не в списке порядка (например, NEW) — считаем фичу готовой
            return False

        for next_stage in self.stage_order[current_idx+1:]:
            if next_stage in self.remaining:
                self.current_stage = next_stage
                return True
        return False

    def reset_worked_today(self):
        """Сбросить флаг worked_today (вызывается в начале нового дня)."""
        self.worked_today = False

    def is_completely_done(self) -> bool:
        """Проверить, полностью ли завершена фича."""
        return all(rem <= 0 for rem in self.remaining.values())