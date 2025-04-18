# Инструкция по запуску тестов

1. Клонируйте репозиторий:

``` bash
git clone https://github.com/NikitaNedelko/kaspersky-config-test.git
```

2. Перейдите в папку проекта:

``` bash
cd kaspersky_config_test
```
   
3. Создайте виртуальное окружение:

``` bash
python3 -m venv venv_linux
source venv_linux/bin/activate
```

4. Установите зависимости:

``` bash
pip install -r requirements.txt
```

5. Убедитесь, что переменная CONFIG_PATH указывает на файл конфига.

``` bash
export CONFIG_PATH=/mnt/d/git/kaspersky-config-test/example/valid_config.ini
```

6. Запустите тесты:

``` bash
pytest

pytest --cov=. --cov-report=html tests/ # для просмотра отчета в html

pytest -v --tb=short > result.txt # сохранение артефактов тестов в файл
```

