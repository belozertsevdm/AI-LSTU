def prove_goal(
    rules,
    working_memory,
    goal,
    visited,
    proved,
    level=0
):
    indent = "  " * level

    # Факт уже находится в рабочей БД
    if goal in working_memory:
        print(f"{indent}✓ {goal} — факт известен")
        proved.add(goal)
        return True

    # Факт уже был успешно доказан ранее
    if goal in proved:
        print(f"{indent}✓ {goal} — уже доказан")
        return True

    # Проверка на настоящий цикл
    if goal in visited:
        print(f"{indent}✗ {goal} — обнаружен цикл")
        return False

    print(f"{indent}→ Требуется доказать: {goal}")

    # Добавляем цель в текущий путь доказательства
    visited.add(goal)

    # Ищем правила, которые могут получить эту цель
    matching_rules = find_rules_for_goal(rules, goal)

    if not matching_rules:
        print(
            f"{indent}✗ Нет правила, "
            f"которое выводит {goal}"
        )
        visited.remove(goal)
        return False

    # Проверяем подходящие правила
    for rule in matching_rules:

        print(
            f"{indent}Проверяем правило "
            f"{rule.rule_id}"
        )

        all_conditions_proved = True

        for condition in rule.conditions:

            if not prove_goal(
                rules,
                working_memory,
                condition,
                visited,
                proved,
                level + 1
            ):
                all_conditions_proved = False
                break

        if all_conditions_proved:

            print(
                f"{indent}✓ Правило {rule.rule_id} "
                f"доказывает {goal}"
            )

            proved.add(goal)
            visited.remove(goal)

            return True

    print(
        f"{indent}✗ Не удалось доказать {goal}"
    )

    visited.remove(goal)

    return False

def find_rules_for_goal(rules, goal):
    """
    Возвращает правила, заключением которых является goal.
    """

    result = []

    for rule in rules:
        if rule.conclusion == goal:
            result.append(rule)

    return result


def backward_chain(rules, working_memory, goal):
    print("\n=== ОБРАТНАЯ ЦЕПОЧКА РАССУЖДЕНИЙ ===")
    print(f"Цель: {goal}\n")

    visited = set()
    proved = set()

    result = prove_goal(
        rules,
        working_memory,
        goal,
        visited,
        proved,
        level=0
    )

    if result:
        print("\nЦЕЛЬ ДОКАЗАНА.")
        return True

    print("\nЦЕЛЬ НЕ ДОКАЗАНА.")
    return False