import numpy as np


class FuzzySet:
    """Нечеткое множество с треугольной функцией принадлежности."""

    def __init__(self, name, f_type, params):
        self.name = name
        self.f_type = f_type
        self.params = [float(p) for p in params]
        if self.f_type != "Треугольник" or len(self.params) != 3:
            raise ValueError(
                f"Для терма {name} требуется тип Треугольник и 3 параметра"
            )
        a, b, c = self.params
        if not a <= b <= c:
            raise ValueError(
                f"Некорректные параметры терма {name}: требуется a <= b <= c"
            )

    def membership(self, x):
        a, b, c = self.params

        # Левые и правые плечи треугольной функции.
        if a == b and x <= b:
            return 1.0 if x <= b else 0.0
        if b == c and x >= b:
            return 1.0 if x >= b else 0.0

        if x < a or x > c:
            return 0.0
        if x == b:
            return 1.0
        if x < b:
            return (x - a) / (b - a) if b != a else 1.0
        return (c - x) / (c - b) if c != b else 1.0


class FuzzyVariable:
    def __init__(self, name, min_val, max_val):
        self.name = name
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.terms = {}

    def fuzzify(self, value):
        if not self.min_val <= value <= self.max_val:
            raise ValueError(
                f"Значение переменной {self.name} должно быть "
                f"в диапазоне {self.min_val:g}...{self.max_val:g}"
            )
        return {name: fs.membership(value) for name, fs in self.terms.items()}


class Rule:
    def __init__(self, conditions, conclusion):
        self.conditions = conditions
        self.conclusion = conclusion

    def get_weight(self, fuzzified_inputs, agg_op="min"):
        weights = [
            fuzzified_inputs.get(var, {}).get(term, 0.0)
            for var, term in self.conditions
        ]
        if not weights:
            return 0.0
        if agg_op == "min":
            return min(weights)
        if agg_op == "prod":
            return float(np.prod(weights))
        raise ValueError(f"Неизвестный оператор агрегации условий: {agg_op}")


class FuzzySystem:
    def __init__(self):
        self.variables = {}
        self.rules = []

    def load_from_file(self, filename):
        self.variables = {}
        self.rules = []
        current_var = None

        with open(filename, "r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                try:
                    if parts[0] == "VAR":
                        if len(parts) != 4:
                            raise ValueError("формат VAR: VAR имя минимум максимум")
                        var_name = parts[1]
                        current_var = FuzzyVariable(
                            var_name, float(parts[2]), float(parts[3])
                        )
                        self.variables[var_name] = current_var

                    elif parts[0] == "TERM":
                        if len(parts) != 6:
                            raise ValueError(
                                "формат TERM: TERM имя тип a b c"
                            )
                        if current_var is None:
                            raise ValueError("TERM должен следовать за VAR")
                        term_name, f_type = parts[1], parts[2]
                        current_var.terms[term_name] = FuzzySet(
                            term_name, f_type, parts[3:]
                        )

                    elif line.startswith("ЕСЛИ "):
                        if " ТО " not in line:
                            raise ValueError("в правиле отсутствует ТО")
                        cond_str, concl_str = line[5:].split(" ТО ", 1)
                        conditions = []
                        for condition in cond_str.split(" И "):
                            if "=" not in condition:
                                raise ValueError("условие должно иметь вид Переменная=Терм")
                            var, term = condition.split("=", 1)
                            conditions.append((var.strip(), term.strip()))
                        if "=" not in concl_str:
                            raise ValueError("заключение должно иметь вид Переменная=Терм")
                        out_var, out_term = concl_str.split("=", 1)
                        rule = Rule(
                            conditions,
                            (out_var.strip(), out_term.strip())
                        )
                        self.rules.append(rule)
                    else:
                        raise ValueError(f"неизвестная директива: {parts[0]}")

                except (ValueError, IndexError) as exc:
                    raise ValueError(
                        f"Ошибка в строке {line_number}: {exc}"
                    ) from exc

        if not self.variables:
            raise ValueError("В файле не объявлены переменные")
        if not self.rules:
            raise ValueError("В файле не объявлены правила")

        # Проверка ссылок на переменные и термы.
        for number, rule in enumerate(self.rules, start=1):
            for var_name, term_name in rule.conditions + [rule.conclusion]:
                if var_name not in self.variables:
                    raise ValueError(
                        f"Правило {number}: неизвестная переменная {var_name}"
                    )
                if term_name not in self.variables[var_name].terms:
                    raise ValueError(
                        f"Правило {number}: у переменной {var_name} "
                        f"нет терма {term_name}"
                    )

    def infer(self, inputs, implication="min", aggregation="max",
              defuzz="centroid", mechanism="mamdani", agg_op="min"):
        if not inputs:
            raise ValueError("Необходимо ввести хотя бы одну входную переменную")

        fuzzified_inputs = {}
        for var_name, value in inputs.items():
            if var_name not in self.variables:
                raise ValueError(f"Неизвестная переменная: {var_name}")
            fuzzified_inputs[var_name] = self.variables[var_name].fuzzify(value)

        output_vars = {rule.conclusion[0] for rule in self.rules}
        if len(output_vars) != 1:
            raise ValueError("В текущей реализации правила должны иметь одну выходную переменную")
        out_var = self.variables[next(iter(output_vars))]

        if mechanism == "truth_levels":
            numerator = 0.0
            denominator = 0.0
            for rule in self.rules:
                weight = rule.get_weight(fuzzified_inputs, agg_op=agg_op)
                if weight > 0:
                    term = out_var.terms[rule.conclusion[1]]
                    center = term.params[1]
                    numerator += weight * center
                    denominator += weight
            return numerator / denominator if denominator else None

        if implication not in {"min", "prod"}:
            raise ValueError("Импликация должна быть min или prod")
        if aggregation not in {"max", "sum"}:
            raise ValueError("Агрегация должна быть max или sum")

        x_values = np.linspace(out_var.min_val, out_var.max_val, 1001)
        aggregated = np.zeros_like(x_values)

        for rule in self.rules:
            weight = rule.get_weight(fuzzified_inputs, agg_op=agg_op)
            if weight <= 0:
                continue
            term = out_var.terms[rule.conclusion[1]]
            y_values = np.array([term.membership(x) for x in x_values])

            if implication == "min":
                y_values = np.minimum(y_values, weight)
            else:  # PRODUCT / Larsen implication
                y_values = y_values * weight

            if aggregation == "max":
                aggregated = np.maximum(aggregated, y_values)
            else:
                aggregated = aggregated + y_values

        if defuzz == "centroid":
            denominator = np.sum(aggregated)
            if denominator == 0:
                return None
            return float(np.sum(x_values * aggregated) / denominator)
        raise ValueError(f"Неизвестный метод дефаззификации: {defuzz}")


def run_all_mechanisms(system, inputs):
    print(f"\nВходные данные: {inputs}")
    print("-" * 64)
    results = [
        ("1. MIN + MAX (Max-Min, Мамдани)",
         system.infer(inputs, implication="min", aggregation="max")),
        ("2. PRODUCT + MAX (Max-Product)",
         system.infer(inputs, implication="prod", aggregation="max")),
        ("3. MIN + SUM (альтернативная агрегация)",
         system.infer(inputs, implication="min", aggregation="sum")),
        ("4. Уровни истинности предпосылок правил",
         system.infer(inputs, mechanism="truth_levels")),
    ]
    for label, value in results:
        rendered = "нет активных правил" if value is None else f"{value:.2f}"
        print(f"{label}: {rendered}")
    print("-" * 64)
    return results


def read_float(prompt, min_val, max_val):
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Введите значение в диапазоне {min_val:g}...{max_val:g}.")
        except ValueError:
            print("Введите число.")


def main():
    system = FuzzySystem()
    try:
        system.load_from_file("rules.txt")
    except (OSError, ValueError) as exc:
        print(f"Не удалось загрузить базу знаний: {exc}")
        return

    print(f"Загружено правил: {len(system.rules)}")
    print("Предметная область: подбор сложности блюда для списка покупок")

    while True:
        print("\n--- МЕНЮ ---")
        print("1. Вывод по одной входной переменной (время готовки)")
        print("2. Вывод по трём входным переменным")
        print("3. Ввести значения вручную")
        print("4. Показать базу правил")
        print("0. Выход")
        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                time = read_float("Время готовки (0...180 минут): ", 0, 180)
                run_all_mechanisms(system, {"Время_готовки": time})
            elif choice == "2":
                time = read_float("Время готовки (0...180 минут): ", 0, 180)
                budget = read_float("Бюджет (0...5000 рублей): ", 0, 5000)
                portions = read_float("Количество порций (1...10): ", 1, 10)
                run_all_mechanisms(system, {
                    "Время_готовки": time,
                    "Бюджет": budget,
                    "Количество_порций": portions,
                })
            elif choice == "3":
                inputs = {}
                print("Можно пропустить переменную клавишей Enter.")
                specs = [
                    ("Время_готовки", "Время готовки", 0, 180),
                    ("Бюджет", "Бюджет", 0, 5000),
                    ("Количество_порций", "Количество порций", 1, 10),
                ]
                for name, label, low, high in specs:
                    raw = input(f"{label} ({low}...{high}): ").strip()
                    if raw:
                        value = float(raw)
                        if not low <= value <= high:
                            raise ValueError(
                                f"{label}: значение должно быть в диапазоне {low}...{high}"
                            )
                        inputs[name] = value
                if inputs:
                    run_all_mechanisms(system, inputs)
                else:
                    print("Не введено ни одной переменной.")
            elif choice == "4":
                print("\nБАЗА ПРАВИЛ")
                for number, rule in enumerate(system.rules, start=1):
                    conditions = " И ".join(f"{v}={t}" for v, t in rule.conditions)
                    out_var, out_term = rule.conclusion
                    print(f"{number:02d}. ЕСЛИ {conditions} ТО {out_var}={out_term}")
            elif choice == "0":
                print("Выход.")
                break
            else:
                print("Неверный выбор.")
        except (ValueError, KeyError) as exc:
            print(f"Ошибка ввода или вывода: {exc}")


if __name__ == "__main__":
    main()
