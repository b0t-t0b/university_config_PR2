import sys
import json
import urllib.request
import urllib.error
from urllib.parse import quote


class CLI_JavaScript:
    def __init__(self):
        try:
            self.params = self.parse_arguments()
            self.validate_arguments(self.params)
            self.print_params()
            self.stage2_get_dependencies()
        except Exception as e:
            print(f"Ошибка конфигурации: {e}")
            sys.exit(1)

    def parse_arguments(self):
        """Парсинг аргументов командной строки вручную"""
        args = sys.argv[1:]
        params = {
            'package_name': None,
            'repo_url': None,
            'test_mode': False  # Оставляем, но не используем в этапе 2
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
Использование:
  python main.py --package-name NAME --repo-url URL

Параметры:
  --package-name, -p    Имя анализируемого пакета
  --repo-url, -r        URL-адрес репозитория
  --help, -h            Показать справку
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

    def print_params(self):
        print("Настроенные параметры (ключ-значение):")
        print("=" * 40)
        print(f"package_name: {self.params['package_name']}")
        print(f"repo_url: {self.params['repo_url']}")
        print("=" * 40)

    def stage2_get_dependencies(self):
        """Этап 2: Получение прямых зависимостей пакета"""
        print("\n=== ЭТАП 2: Сбор данных ===")
        self._get_dependencies_from_source_repo()

    def _get_dependencies_from_source_repo(self):
        """Получение зависимостей напрямую из исходного репозитория"""
        package_name = self.params['package_name']
        repo_url = self.params['repo_url']

        try:
            print(f"Получение зависимостей для пакета {package_name} из репозитория...")

            # Определяем тип репозитория и формируем URL к package.json
            if 'github.com' in repo_url:
                if repo_url.endswith('.git'):
                    repo_url = repo_url[:-4]
                raw_url = repo_url.replace('github.com', 'raw.githubusercontent.com') + '/main/package.json'
            elif 'gitlab.com' in repo_url:
                raw_url = repo_url + '/-/raw/main/package.json'
            else:
                raw_url = repo_url if repo_url.endswith('package.json') else repo_url + '/package.json'

            print(f"Запрос package.json из: {raw_url}")

            req = urllib.request.Request(
                raw_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    raise ValueError(f"Ошибка при запросе package.json: {response.status}")

                data = response.read().decode('utf-8')
                package_data = json.loads(data)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            print(f"\nПрямые зависимости пакета '{package_name}':")
            print("-" * 50)

            if dependencies:
                print("dependencies:")
                for dep_name, dep_version in dependencies.items():
                    print(f"  {dep_name}: {dep_version}")

            if dev_dependencies:
                print("devDependencies:")
                for dep_name, dep_version in dev_dependencies.items():
                    print(f"  {dep_name}: {dep_version}")

            if not dependencies and not dev_dependencies:
                print("  Прямые зависимости отсутствуют")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"package.json не найден в репозитории")
            else:
                raise ValueError(f"Ошибка HTTP при запросе package.json: {e.code}")
        except urllib.error.URLError as e:
            raise ValueError(f"Ошибка сети: {e.reason}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга package.json: {e}")
        except Exception as e:
            raise ValueError(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    cli = CLI_JavaScript()