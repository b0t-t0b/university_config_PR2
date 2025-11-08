import sys

class CLI_JavaScript:
    def __init__(self):
        try:
            self.params = self.parse_arguments()
            self.validate_arguments(self.params)
            self.print_params()
        except Exception as e:
            print(f"Ошибка конфигурации: {e}")
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
                    params['package_name'] = ""  # Явно устанавливаем пустую строку

            elif arg in ['--repo-url', '-r']:
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    params['repo_url'] = args[i + 1]
                    i += 1
                else:
                    params['repo_url'] = ""  # Явно устанавливаем пустую строку

            elif arg in ['--test-mode', '-t']:
                params['test_mode'] = True


            i += 1

        return params

    def validate_arguments(self, params):
        """Валидация аргументов командной строки"""
        errors = []

        # Проверка имени пакета
        if params['package_name'] is None:
            errors.append("Не указано имя пакета (используйте --package-name или -p)")
        elif params['package_name'] == "":
            errors.append("Имя пакета не может быть пустым")

        # Проверка URL/пути репозитория
        if params['repo_url'] is None:
            errors.append("Не указан URL репозитория (используйте --repo-url или -r)")
        elif params['repo_url'] == "":
            errors.append("URL репозитория не может быть пустым")

        # Если есть ошибки - выводим их все
        if errors:
            error_msg = "\n".join([f"  - {error}" for error in errors])
            raise ValueError(f"Обнаружены ошибки в параметрах:\n{error_msg}")

    def print_params(self):
        print("Настроенные параметры (ключ-значение):")
        print("=" * 40)
        print(f"package_name: {self.params['package_name']}")
        print(f"repo_url: {self.params['repo_url']}")
        print(f"test_mode: {self.params['test_mode']}")
        print("=" * 40)


if __name__ == "__main__":
    cli = CLI_JavaScript()