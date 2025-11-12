import sys
from collections import deque


class CLI_JavaScript:
    def __init__(self):
        try:
            self.params = self.parse_arguments()
            self.validate_arguments(self.params)

            if self.params['test_mode']:
                # В тестовом режиме выполняем Этапы 3 и 4
                self.stage3_build_dependency_graph()
                self.stage4_reverse_dependencies()
            else:
                # В реальном режиме только Этап 2
                self.stage2_get_dependencies_real()

        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)

    def parse_arguments(self):
        """Парсинг аргументов командной строки вручную"""
        args = sys.argv[1:]
        params = {
            'package_name': None,
            'repo_url': None,
            'test_mode': False
        }

        i = 0
        while i < len(args):
            arg = args[i]

            if arg in ['--package-name', '-p']:
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    params['package_name'] = args[i + 1]
                    i += 1
                else:
                    params['package_name'] = ""

            elif arg in ['--repo-url', '-r']:
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    params['repo_url'] = args[i + 1]
                    i += 1
                else:
                    params['repo_url'] = ""

            elif arg in ['--test-mode', '-t']:
                params['test_mode'] = True

            elif arg in ['--help', '-h']:
                self.print_help()
                sys.exit(0)

            i += 1

        return params

    def print_help(self):
        """Вывод справки"""
        help_text = """
Инструмент визуализации графа зависимостей для менеджера пакетов (JavaScript/npm)

Использование:
  Этап 2 (реальный режим):
    python main.py --package-name NAME --repo-url URL

  Этапы 3-4 (тестовый режим):
    python main.py --package-name NAME --repo-url FILE --test-mode

Параметры:
  --package-name, -p    Имя анализируемого пакета
  --repo-url, -r        URL репозитория (режим) или путь к файлу (тестовый режим)
  --test-mode, -t       Активировать тестовый режим работы с файлом графа
  --help, -h            Показать справку

Примеры:
  Этап 2: python main.py -p "react" -r "https://github.com/facebook/react"
  Этапы 3-4: python main.py -p "A" -r "graph.txt" -t
        """
        print(help_text.strip())

    def validate_arguments(self, params):
        """Валидация аргументов командной строки"""
        errors = []

        if params['package_name'] is None:
            errors.append("Не указано имя пакета (используйте --package-name или -p)")
        elif params['package_name'] == "":
            errors.append("Имя пакета не может быть пустым")
        elif len(params['package_name'].strip()) == 0:
            errors.append("Имя пакета не может состоять только из пробелов")

        if params['repo_url'] is None:
            errors.append("Не указан URL репозитория (используйте --repo-url или -r)")
        elif params['repo_url'] == "":
            errors.append("URL репозитория не может быть пустым")
        elif len(params['repo_url'].strip()) == 0:
            errors.append("URL репозитория не может состоять только из пробелов")

        if errors:
            error_msg = "\n".join([f"  - {error}" for error in errors])
            raise ValueError(f"Обнаружены ошибки в параметрах:\n{error_msg}")

    def stage2_get_dependencies_real(self):
        """Этап 2: Реальный режим - получение зависимостей из репозитория"""
        print("\n=== ЭТАП 2: Сбор данных ===")
        print("Этап 2 выполняется в реальном режиме...")
        print("Для Этапов 3-4 используйте тестовый режим с флагом -t")

    def stage3_build_dependency_graph(self):
        """Этап 3: Построение графа зависимостей с учетом транзитивности"""
        print("\n=== ЭТАП 3: Основные операции ===")

        print("Построение графа зависимостей с учетом транзитивности...")

        # Читаем граф из файла
        self.graph = self._read_dependency_graph()
        start_package = self.params['package_name']

        # Проверяем, что стартовый пакет есть в графе
        if start_package not in self.graph:
            raise ValueError(f"Пакет '{start_package}' не найден в графе зависимостей")

        # Строим полный граф зависимостей с помощью BFS с рекурсией
        print(f"\nПостроение графа зависимостей для пакета '{start_package}'...")
        self.full_graph = self._build_transitive_dependencies_bfs_recursive(self.graph, start_package)

        # Выводим результат
        self._print_dependency_graph(self.full_graph, start_package)

        # Демонстрируем обработку циклических зависимостей в ПОСТРОЕННОМ графе
        self._demo_cycle_handling(self.full_graph)

    def stage4_reverse_dependencies(self):
        """Этап 4: Поиск обратных зависимостей"""
        print("\n=== ЭТАП 4: Дополнительные операции ===")

        target_package = self.params['package_name']
        print(f"Поиск обратных зависимостей для пакета '{target_package}'...")
        print("(пакеты, которые зависят от данного пакета)")

        # Находим все пакеты, которые зависят от целевого пакета
        reverse_dependencies = self._find_reverse_dependencies(target_package)

        # Выводим результат
        self._print_reverse_dependencies(reverse_dependencies, target_package)

        # Демонстрируем на различных случаях
        self._demo_reverse_dependencies_cases()

    def _read_dependency_graph(self):
        """Чтение графа зависимостей из тестового файла"""
        file_path = self.params['repo_url']
        graph = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue

                    parts = line.split(':', 1)
                    package = parts[0].strip()
                    dependencies = [dep.strip() for dep in parts[1].split(',')] if parts[1].strip() else []

                    graph[package] = dependencies

            print(f"Загружен граф из {len(graph)} пакетов")

        except FileNotFoundError:
            raise ValueError(f"Файл графа зависимостей не найден: {file_path}")
        except Exception as e:
            raise ValueError(f"Ошибка чтения графа зависимостей: {e}")

        return graph

    def _build_transitive_dependencies_bfs_recursive(self, graph, start_package):
        """Построение транзитивных зависимостей с помощью BFS с рекурсией"""
        visited = set()
        result_graph = {}

        def bfs_recursive(current_level):
            if not current_level:
                return

            next_level = []

            for package in current_level:
                if package in visited:
                    continue

                visited.add(package)
                result_graph[package] = graph.get(package, [])

                # Добавляем зависимости в следующий уровень
                for dep in graph.get(package, []):
                    if dep not in visited and dep not in next_level:
                        next_level.append(dep)

            # Рекурсивный вызов для следующего уровня
            bfs_recursive(next_level)

        # Запускаем BFS с рекурсией
        bfs_recursive([start_package])

        return result_graph

    def _find_reverse_dependencies(self, target_package):
        """Поиск всех пакетов, которые зависят от целевого пакета"""
        reverse_deps = []

        # Проходим по всем пакетам в графе и ищем те, которые зависят от target_package
        for package, dependencies in self.graph.items():
            # Используем BFS для поиска target_package в зависимостях текущего пакета
            if self._has_dependency_bfs_recursive(package, target_package):
                if package != target_package:  # Исключаем сам пакет
                    reverse_deps.append(package)

        return reverse_deps

    def _has_dependency_bfs_recursive(self, start_package, target_dependency):
        """Проверяет, зависит ли пакет от целевой зависимости (использует BFS с рекурсией)"""
        visited = set()

        def bfs_recursive(current_level):
            if not current_level:
                return False

            next_level = []

            for package in current_level:
                if package in visited:
                    continue

                visited.add(package)

                # Если нашли целевую зависимость
                if package == target_dependency:
                    return True

                # Добавляем зависимости в следующий уровень
                for dep in self.graph.get(package, []):
                    if dep not in visited and dep not in next_level:
                        next_level.append(dep)

            # Рекурсивный вызов для следующего уровня
            return bfs_recursive(next_level)

        # Запускаем BFS с рекурсией
        return bfs_recursive([start_package])

    def _print_dependency_graph(self, graph, start_package):
        """Вывод графа зависимостей"""
        print(f"\nПолный граф зависимостей для пакета '{start_package}':")
        print("=" * 60)

        packages = list(graph.keys())
        packages.sort()

        for package in packages:
            dependencies = graph[package]
            if dependencies:
                print(f"{package} -> {', '.join(dependencies)}")
            else:
                print(f"{package} -> (нет зависимостей)")

        print(f"\nСтатистика:")
        print(f"  Всего пакетов в графе: {len(graph)}")
        print(f"  Стартовый пакет: {start_package}")

    def _print_reverse_dependencies(self, reverse_deps, target_package):
        """Вывод обратных зависимостей"""
        print(f"\nОбратные зависимости для пакета '{target_package}':")
        print("=" * 60)

        if reverse_deps:
            reverse_deps.sort()
            for i, package in enumerate(reverse_deps, 1):
                print(f"  {i}. {package}")

            print(f"\nСтатистика:")
            print(f"  Всего пакетов, зависящих от '{target_package}': {len(reverse_deps)}")
        else:
            print("  Обратные зависимости не обнаружены")
            print(f"  Ни один пакет не зависит от '{target_package}'")

    def _demo_cycle_handling(self, graph):
        """Демонстрация обработки циклических зависимостей"""
        print("\n" + "=" * 60)
        print("Демонстрация обработки циклических зависимостей")
        print("=" * 60)

        # Проверяем наличие циклов в графе
        cycles = self._find_cycles(graph)

        if cycles:
            print("Обнаружены циклические зависимости:")
            for i, cycle in enumerate(cycles, 1):
                # Убедимся, что цикл полный (замыкается)
                if len(cycle) > 1 and cycle[0] != cycle[-1]:
                    cycle.append(cycle[0])
                print(f"  Цикл {i}: {' -> '.join(cycle)}")

            print(f"\nВсего обнаружено циклов: {len(cycles)}")
        else:
            print("Циклические зависимости не обнаружены")

    def _demo_reverse_dependencies_cases(self):
        print("\n" + "=" * 60)
        print("Демонстрация обратных зависимостей на различных случаях")
        print("=" * 60)

        target_package = self.params['package_name']

        # Уточняем, что это статистика по ВСЕМУ графу
        print("Статистика по ВСЕМУ графу:")

        # Показываем прямые обратные зависимости
        direct_reverse = []
        for package, dependencies in self.graph.items():
            if target_package in dependencies and package != target_package:
                direct_reverse.append(package)

        if direct_reverse:
            print(f"Прямые обратные зависимости '{target_package}': {', '.join(sorted(direct_reverse))}")
        else:
            print(f"Прямые обратные зависимости '{target_package}': отсутствуют")

        # Находим пакеты с максимальным количеством обратных зависимостей
        max_reverse_deps = 0
        popular_packages = []

        for package in self.graph:
            reverse_deps = self._find_reverse_dependencies(package)
            count = len(reverse_deps)

            if count > max_reverse_deps:
                max_reverse_deps = count
                popular_packages = [package]
            elif count == max_reverse_deps and count > 0:
                popular_packages.append(package)

        if popular_packages and max_reverse_deps > 0:
            print(f"\nПакеты с наибольшим количеством обратных зависимостей ({max_reverse_deps}):")
            for package in sorted(popular_packages):
                print(f"  - {package}")

        # Находим пакеты без обратных зависимостей (листья)
        leaf_packages = []
        for package in self.graph:
            reverse_deps = self._find_reverse_dependencies(package)
            if len(reverse_deps) == 0:
                leaf_packages.append(package)

        if leaf_packages:
            leaf_packages.sort()
            print(f"\nПакеты без обратных зависимостей (листья, всего {len(leaf_packages)}):")
            if len(leaf_packages) <= 10:
                for package in leaf_packages:
                    print(f"  - {package}")
            else:
                print(f"  (показаны первые 10 из {len(leaf_packages)})")
                for package in leaf_packages[:10]:
                    print(f"  - {package}")

    def _find_cycles(self, graph):
        """Поиск циклических зависимостей в графе"""

        def dfs(node, path, visited, rec_stack, cycles):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path, visited, rec_stack, cycles)
                elif neighbor in rec_stack:
                    # Найден цикл - создаем полный цикл
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]  # Замыкаем цикл
                    # Проверяем, что цикл не дублируется
                    if cycle not in cycles:
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        visited = set()
        rec_stack = set()
        cycles = []

        for node in graph:
            if node not in visited:
                dfs(node, [], visited, rec_stack, cycles)

        return cycles


if __name__ == "__main__":
    cli = CLI_JavaScript()