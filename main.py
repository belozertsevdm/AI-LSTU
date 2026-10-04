from rules_manager import (
    Rule,
    load_rules,
    save_rules,
    add_rule,
    edit_rule,
    delete_rule
)

from inference import forward_chaining
from backward_inference import backward_chain


RULES_FILE = "rules.txt"


def show_rules(rules):
    print("\n=== БАЗА ПРАВИЛ ===")

    if not rules:
        print("База правил пуста.")
        return

    for rule in rules:
        print(rule)


def show_working_memory(working_memory):
    print("\n=== РАБОЧАЯ БАЗА ДАННЫХ ===")

    if not working_memory:
        print("Рабочая база данных пуста.")
        return

    for fact in sorted(working_memory):
        print(f"- {fact}")


def show_menu():
    print("""
=== ЭКСПЕРТНАЯ СИСТЕМА ===

1. Задать начальную ситуацию
2. Показать рабочую базу данных
3. Запустить прямую цепочку рассуждений
4. Запустить обратную цепочку рассуждений
5. Показать базу правил
6. Добавить правило
7. Изменить правило
8. Удалить правило
9. Очистить рабочую базу данных
0. Выход
""")


def add_rule_menu(rules):
    print("\n=== ДОБАВЛЕНИЕ ПРАВИЛА ===")

    rule_id = input("Введите ID правила: ").strip()

    conditions_text = input(
        "Введите условия через &: "
    ).strip()

    conclusion = input(
        "Введите вывод: "
    ).strip()

    conditions = [
        condition.strip()
        for condition in conditions_text.split("&")
    ]

    try:
        rule = Rule(
            rule_id,
            conditions,
            conclusion
        )

        add_rule(rules, rule)
        save_rules(RULES_FILE, rules)

        print("Правило успешно добавлено.")

    except ValueError as error:
        print(f"Ошибка: {error}")


def edit_rule_menu(rules):
    print("\n=== ИЗМЕНЕНИЕ ПРАВИЛА ===")

    rule_id = input("Введите ID правила: ").strip()

    conditions_text = input(
        "Введите новые условия через &: "
    ).strip()

    conclusion = input(
        "Введите новый вывод: "
    ).strip()

    conditions = [
        condition.strip()
        for condition in conditions_text.split("&")
    ]

    try:
        edit_rule(
            rules,
            rule_id,
            conditions,
            conclusion
        )

        save_rules(RULES_FILE, rules)

        print("Правило успешно изменено.")

    except ValueError as error:
        print(f"Ошибка: {error}")


def delete_rule_menu(rules):
    print("\n=== УДАЛЕНИЕ ПРАВИЛА ===")

    rule_id = input("Введите ID правила: ").strip()

    try:
        delete_rule(rules, rule_id)
        save_rules(RULES_FILE, rules)

        print("Правило успешно удалено.")

    except ValueError as error:
        print(f"Ошибка: {error}")


def main():

    # Загрузка базы правил
    try:
        rules = load_rules(RULES_FILE)

    except (FileNotFoundError, ValueError) as error:
        print(f"Ошибка загрузки: {error}")
        return

    # Рабочая база данных
    working_memory = set()

    while True:

        show_menu()

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print("\n=== НАЧАЛЬНАЯ СИТУАЦИЯ ===")
            print("Введите факты через запятую.")

            text = input("> ").strip()

            working_memory = {
                fact.strip()
                for fact in text.split(",")
                if fact.strip()
            }

            print("Начальная ситуация установлена.")

        elif choice == "2":
            show_working_memory(working_memory)

        elif choice == "3":
            forward_chaining(
                rules,
                working_memory
            )

        elif choice == "4":
            print("\n=== ОБРАТНАЯ ЦЕПОЧКА РАССУЖДЕНИЙ ===")

            goal = input(
                "Введите целевую ситуацию: "
            ).strip()

            if not goal:
                print("Цель не может быть пустой.")
            else:
                backward_chain(
                    rules,
                    working_memory,
                    goal
                )

        elif choice == "5":
            show_rules(rules)

        elif choice == "6":
            add_rule_menu(rules)

        elif choice == "7":
            edit_rule_menu(rules)

        elif choice == "8":
            delete_rule_menu(rules)

        elif choice == "9":
            working_memory.clear()
            print("Рабочая база данных очищена.")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()