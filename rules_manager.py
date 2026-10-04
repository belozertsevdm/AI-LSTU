class Rule:
    def __init__(self, rule_id, conditions, conclusion):
        self.rule_id = rule_id
        self.conditions = conditions
        self.conclusion = conclusion

    def __str__(self):
        conditions = " & ".join(self.conditions)
        return f"{self.rule_id} | {conditions} | {self.conclusion}"


def validate_rule(rule, existing_ids=None):
    if not rule.rule_id:
        raise ValueError(
            "ID правила не может быть пустым"
        )

    if existing_ids is not None:
        if rule.rule_id in existing_ids:
            raise ValueError(
                f"ID правила {rule.rule_id} уже существует"
            )

    if not rule.conditions:
        raise ValueError(
            f"У правила {rule.rule_id} отсутствуют условия"
        )

    for condition in rule.conditions:
        if not condition.strip():
            raise ValueError(
                f"У правила {rule.rule_id} "
                f"обнаружено пустое условие"
            )

    if not rule.conclusion.strip():
        raise ValueError(
            f"У правила {rule.rule_id} отсутствует вывод"
        )


def load_rules(filename):
    rules = []
    rule_ids = set()

    try:
        with open(filename, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                parts = line.split("|")

                if len(parts) != 3:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"неправильный формат правила"
                    )

                rule_id = parts[0].strip()
                conditions_text = parts[1].strip()
                conclusion = parts[2].strip()

                if not rule_id:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"отсутствует ID правила"
                    )

                if rule_id in rule_ids:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"ID правила {rule_id} "
                        f"уже существует"
                    )

                if not conditions_text:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"отсутствует условие"
                    )

                conditions = [
                    condition.strip()
                    for condition in conditions_text.split("&")
                ]

                if any(not condition for condition in conditions):
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"обнаружено пустое условие"
                    )

                if not conclusion:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: "
                        f"отсутствует вывод"
                    )

                rule = Rule(
                    rule_id,
                    conditions,
                    conclusion
                )

                rules.append(rule)
                rule_ids.add(rule_id)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Файл базы правил '{filename}' не найден"
        )

    return rules


def save_rules(filename, rules):
    rule_ids = set()

    for rule in rules:
        validate_rule(rule, rule_ids)
        rule_ids.add(rule.rule_id)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("# База правил экспертной системы\n")
        file.write("# Формат: ID | УСЛОВИЯ | ВЫВОД\n\n")

        for rule in rules:
            conditions = " & ".join(rule.conditions)

            file.write(
                f"{rule.rule_id} | "
                f"{conditions} | "
                f"{rule.conclusion}\n"
            )


def get_rule(rules, rule_id):
    for rule in rules:
        if rule.rule_id == rule_id:
            return rule

    return None


def add_rule(rules, rule):
    existing_ids = {r.rule_id for r in rules}

    validate_rule(rule, existing_ids)

    rules.append(rule)


def edit_rule(rules, rule_id, conditions, conclusion):
    rule = get_rule(rules, rule_id)

    if rule is None:
        raise ValueError(
            f"Правило {rule_id} не найдено"
        )

    new_rule = Rule(
        rule_id,
        conditions,
        conclusion
    )

    validate_rule(new_rule)

    index = rules.index(rule)
    rules[index] = new_rule


def delete_rule(rules, rule_id):
    rule = get_rule(rules, rule_id)

    if rule is None:
        raise ValueError(
            f"Правило {rule_id} не найдено"
        )

    rules.remove(rule)