#!/usr/bin/env python3
"""
Универсальный скрипт запуска проекта Purchases
Автоматически определяет режим запуска (локально/сервер) и запускает соответствующие службы
"""

import os
import sys
import subprocess
import argparse
import time
import signal
import socket
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


class ProjectStarter:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.is_server = self._detect_server_environment()
        self.processes = []
        self.venv_python = self._get_venv_python()
        
    def _detect_server_environment(self):
        """Определяет, запускается ли проект на сервере"""
        # Явное указание production режима
        if os.environ.get('DJANGO_ENV') == 'production':
            return True
        
        # Проверяем специфичные индикаторы облачных платформ
        cloud_indicators = [
            os.environ.get('RAILWAY_ENVIRONMENT'),
            os.environ.get('HEROKU_APP_NAME'),
            os.environ.get('VERCEL'),
            os.environ.get('AWS_EXECUTION_ENV'),
            os.environ.get('GOOGLE_CLOUD_PROJECT'),
        ]
        
        # По умолчанию - режим разработки
        return any(cloud_indicators)
    
    def _get_venv_python(self):
        """Получает путь к Python в виртуальном окружении"""
        venv_paths = [
            self.base_dir / 'venv' / 'bin' / 'python',
            self.base_dir / '.venv' / 'bin' / 'python',
            self.base_dir / 'env' / 'bin' / 'python',
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists():
                print(f"✅ Найдено виртуальное окружение: {venv_path}")
                return str(venv_path)
        
        print("⚠️ Виртуальное окружение не найдено, создаем новое...")
        return self._create_venv()
    
    def _create_venv(self):
        """Создает виртуальное окружение"""
        venv_path = self.base_dir / 'venv'
        try:
            print("🔧 Создание виртуального окружения...")
            subprocess.run([
                sys.executable, '-m', 'venv', str(venv_path)
            ], check=True)
            
            python_path = venv_path / 'bin' / 'python'
            if python_path.exists():
                print(f"✅ Виртуальное окружение создано: {python_path}")
                return str(python_path)
            else:
                print("❌ Ошибка: не удалось найти Python в созданном окружении")
                return sys.executable
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка создания виртуального окружения: {e}")
            return sys.executable
    
    def _check_port(self, port, service_name):
        """Проверяет доступность порта"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    print(f"⚠️ Порт {port} уже занят ({service_name})")
                    return False
                else:
                    print(f"✅ Порт {port} доступен для {service_name}")
                    return True
        except Exception as e:
            print(f"❌ Ошибка проверки порта {port}: {e}")
            return False
    
    def check_requirements(self):
        """Проверяет наличие всех необходимых зависимостей"""
        print("🔍 Проверка зависимостей...")
        
        # Проверяем Python зависимости
        requirements_file = self.base_dir / 'requirements.txt'
        if requirements_file.exists():
            try:
                print(f"📦 Устанавливаем Python зависимости через {self.venv_python}...")
                subprocess.run([
                    self.venv_python, '-m', 'pip', 'install', '-r', str(requirements_file)
                ], check=True, cwd=self.base_dir)
                print("✅ Python зависимости установлены")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка установки Python зависимостей: {e}")
                print("💡 Попробуйте активировать виртуальное окружение: source venv/bin/activate")
                return False
        
        # Проверяем Node.js зависимости
        package_json = self.base_dir / 'package.json'
        if package_json.exists():
            try:
                subprocess.run(['npm', 'install'], check=True, cwd=self.base_dir)
                print("✅ Node.js зависимости установлены")
            except subprocess.CalledProcessError:
                print("❌ Ошибка установки Node.js зависимостей")
                return False
        
        return True
    
    def setup_environment(self):
        """Настраивает окружение для запуска"""
        print("⚙️ Настройка окружения...")
        
        # Создаем .env файл если его нет
        env_file = self.base_dir / '.env'
        if not env_file.exists():
            env_content = f"""
DEBUG={'False' if self.is_server else 'True'}
SECRET_KEY=your-secret-key-here-please-change-in-production
ALLOWED_HOSTS={'*' if not self.is_server else 'localhost,127.0.0.1'}
DATABASE_URL=sqlite:///{self.base_dir}/db.sqlite3
"""
            env_file.write_text(env_content.strip())
            print("✅ Создан файл .env")
        
        # Применяем миграции
        try:
            print("🔄 Применяем миграции базы данных...")
            subprocess.run([
                self.venv_python, 'manage.py', 'migrate'
            ], check=True, cwd=self.base_dir)
            print("✅ Миграции применены")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка применения миграций: {e}")
            return False
        
        # Собираем статические файлы для продакшена
        if self.is_server:
            try:
                print("📁 Собираем статические файлы...")
                subprocess.run([
                    self.venv_python, 'manage.py', 'collectstatic', '--noinput'
                ], check=True, cwd=self.base_dir)
                print("✅ Статические файлы собраны")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка сборки статических файлов: {e}")
                return False
        
        return True
    
    def build_frontend(self):
        """Сборка frontend части"""
        print("🏗️ Сборка frontend...")
        
        # Собираем Tailwind CSS
        try:
            subprocess.run([
                'npx', 'tailwindcss', '-i', './static/src/input.css', 
                '-o', './static/css/output.css', '--watch' if not self.is_server else '--minify'
            ], check=True, cwd=self.base_dir)
            print("✅ Tailwind CSS собран")
        except subprocess.CalledProcessError:
            print("❌ Ошибка сборки Tailwind CSS")
            return False
        
        return True
    
    def start_django(self):
        """Запускает Django сервер"""
        if self.is_server:
            # Продакшен режим - используем gunicorn
            cmd = [
                'gunicorn', 
                'purchases_project.wsgi:application',
                '--bind', '0.0.0.0:8000',
                '--workers', '3',
                '--timeout', '120'
            ]
        else:
            # Режим разработки
            cmd = [
                self.venv_python, 'manage.py', 'runserver', '0.0.0.0:8000'
            ]
        
        print(f"🚀 Запуск Django {'(production)' if self.is_server else '(development)'}...")
        process = subprocess.Popen(cmd, cwd=self.base_dir)
        self.processes.append(process)
        return process
    
    def start_frontend_dev(self):
        """Запускает frontend разработческий сервер (только для локальной разработки)"""
        if self.is_server:
            return None
            
        print("🎨 Запуск frontend development сервера...")
        
        # Запускаем Tailwind в watch режиме
        cmd = [
            'npx', 'tailwindcss', '-i', './static/src/input.css', 
            '-o', './static/css/output.css', '--watch'
        ]
        
        process = subprocess.Popen(cmd, cwd=self.base_dir)
        self.processes.append(process)
        return process
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print("\n🛑 Получен сигнал завершения...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        sys.exit(0)
    
    def run(self, args):
        """Основной метод запуска"""
        print(f"🎯 Запуск проекта в режиме: {'PRODUCTION' if self.is_server else 'DEVELOPMENT'}")
        
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Проверяем и устанавливаем зависимости
        if not args.skip_deps and not self.check_requirements():
            print("❌ Ошибка проверки зависимостей")
            return 1
        
        # Настраиваем окружение
        if not self.setup_environment():
            print("❌ Ошибка настройки окружения")
            return 1
        
        # Проверяем доступность портов
        if not self._check_port(8000, "Django"):
            print("💡 Попробуйте остановить существующие процессы или использовать другой порт")
            return 1
        
        # Собираем frontend если нужно
        if not args.skip_build:
            if not self.build_frontend():
                print("❌ Ошибка сборки frontend")
                return 1
        
        # Запускаем сервисы
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Запускаем Django
            django_future = executor.submit(self.start_django)
            
            # Запускаем frontend dev сервер если в режиме разработки
            frontend_future = None
            if not self.is_server and not args.backend_only:
                frontend_future = executor.submit(self.start_frontend_dev)
            
            print("✅ Все сервисы запущены!")
            print("📡 Django доступен на: http://localhost:8000")
            
            if not self.is_server:
                print("🎨 Frontend watch режим активен")
                print("💡 Для остановки нажмите Ctrl+C")
            
            try:
                # Ждем завершения процессов
                django_future.result()
                if frontend_future:
                    frontend_future.result()
            except KeyboardInterrupt:
                print("\n🛑 Завершение работы...")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return 1
        
        return 0


def main():
    parser = argparse.ArgumentParser(description='Запуск проекта Purchases')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Пропустить установку зависимостей')
    parser.add_argument('--skip-build', action='store_true', 
                       help='Пропустить сборку frontend')
    parser.add_argument('--backend-only', action='store_true',
                       help='Запустить только backend')
    parser.add_argument('--production', action='store_true',
                       help='Принудительно использовать production режим')
    
    args = parser.parse_args()
    
    # Принудительно устанавливаем production режим если указан флаг
    if args.production:
        os.environ['DJANGO_ENV'] = 'production'
    
    starter = ProjectStarter()
    return starter.run(args)


if __name__ == '__main__':
    sys.exit(main())
