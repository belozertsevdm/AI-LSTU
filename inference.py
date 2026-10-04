def can_fire(rule, working_memory):
    """
    Проверяет, выполняются ли все условия правила.
    """

    for condition in rule.conditions:
        if condition not in working_memory:
            return False

    return True


def forward_chaining(rules, working_memory):
    """
    Выполняет прямую цепочку рассуждений.

    rules:
        список правил экспертной системы

    working_memory:
        множество фактов рабочей базы данных
    """

    print("\n=== ПРЯМАЯ ЦЕПОЧКА РАССУЖДЕНИЙ ===\n")

    changed = True
    fired_rules = []

    while changed:

        changed = False

        for rule in rules:

            # Проверяем возможность срабатывания правила
            if can_fire(rule, working_memory):

                # Если вывод уже есть, новое состояние не возникает
                if rule.conclusion in working_memory:
                    continue

                # Добавляем новый факт
                working_memory.add(rule.conclusion)

                changed = True
                fired_rules.append(rule.rule_id)

                # Выводим информацию о срабатывании
                print(f"Сработало правило {rule.rule_id}:")
                print(
                    f"  Условия: "
                    f"{' & '.join(rule.conditions)}"
                )
                print(
                    f"  Новый факт: {rule.conclusion}"
                )
                print()

    # Результат работы
    if not fired_rules:
        print("Ни одно правило не сработало.")
    else:
        print("Цепочка рассуждений завершена.")
        print(
            f"Всего сработало правил: "
            f"{len(fired_rules)}"
        )

    return working_memory