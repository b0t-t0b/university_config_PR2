import sys
from collections import deque


class CLI_JavaScript:
    def __init__(self):
        try:
            self.params = self.parse_arguments()
            self.validate_arguments(self.params)

            if self.params['test_mode']:
                # В тестовом режиме выполняем только Этап 3
                self.stage3_build_dependency_graph()
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

  Этап 3 (тестовый режим):
    python main.py --package-name NAME --repo-url FILE --test-mode

Параметры:
  --package-name, -p    Имя анализируемого пакета
  --repo-url, -r        URL репозитория (режим) или путь к файлу (тестовый режим)
  --test-mode, -t       Активировать тестовый режим работы с файлом графа
  --help, -h            Показать справку

Примеры:
  Этап 2: python main.py -p "react" -r "https://github.com/facebook/react"
  Этап 3: python main.py -p "A" -r "graph.txt" -t
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
        print("Для Этапа 3 используйте тестовый режим с флагом -t")

    def stage3_build_dependency_graph(self):
        """Этап 3: Построение графа зависимостей с учетом транзитивности"""
        print("\n=== ЭТАП 3: Основные операции ===")

        print("Построение графа зависимостей с учетом транзитивности...")

        # Читаем граф из файла
        graph = self._read_dependency_graph()
        start_package = self.params['package_name']

        # Проверяем, что стартовый пакет есть в графе
        if start_package not in graph:
            raise ValueError(f"Пакет '{start_package}' не найден в графе зависимостей")

        # Строим полный граф зависимостей с помощью BFS с рекурсией
        print(f"\nПостроение графа зависимостей для пакета '{start_package}'...")
        full_graph = self._build_transitive_dependencies_bfs_recursive(graph, start_package)

        # Выводим результат
        self._print_dependency_graph(full_graph, start_package)

        # Демонстрируем обработку циклических зависимостей
        self._demo_cycle_handling(graph)

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
                print(f"  Цикл {i}: {' -> '.join(cycle)}")

            print(f"\nВсего обнаружено циклов: {len(cycles)}")
        else:
            print("Циклические зависимости не обнаружены")

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
                    # Найден цикл
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    # Проверяем, что цикл не дублируется
                    if cycle not in cycles:
                        cycles.append(cycle.copy())

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