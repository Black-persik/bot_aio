import json
import asyncio
import requests
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerfectGPTClient:
    def __init__(self):
        self.api_url = "https://namazlive.herokuapp.com/gpt/generate"
        self.api_key = "jiro_dreams_of_sushi"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        self.app_structure = self._load_app_structure()
        self.perfect_analysis = self._create_perfect_analysis()
        
    
    def _load_app_structure(self) -> Dict:
        try:
            with open('app_structure.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки app_structure.json: {e}")
            return {}
    
    def _create_perfect_analysis(self) -> Dict:
        analysis = {
            'tabs': {},
            'functions': {},
            'articles': {},
            'prayers': {},
            'settings': {},
            'ui_elements': {},
            'navigation_paths': {},
            'search_index': defaultdict(list)
        }
        
        if not self.app_structure:
            print("❌ app_structure.json не загружен")
            return analysis
        
        if isinstance(self.app_structure, list):
            tabs = self.app_structure
            print(f"📁 Структура файла: список, вкладок: {len(tabs)}")
        elif isinstance(self.app_structure, dict):
            print(f"📁 Структура файла: словарь, ключи: {list(self.app_structure.keys())}")
            if 'tabs' in self.app_structure:
                tabs = self.app_structure['tabs']
            elif 'data' in self.app_structure and 'tabs' in self.app_structure['data']:
                tabs = self.app_structure['data']['tabs']
            elif 'app' in self.app_structure and 'tabs' in self.app_structure['app']:
                tabs = self.app_structure['app']['tabs']
            else:
                print("❌ Не найдены вкладки в структуре!")
                return analysis
            print(f"📊 Найдено вкладок: {len(tabs)}")
        else:
            print("❌ Неизвестная структура app_structure.json")
            return analysis
        
        for tab in tabs:
            tab_id = tab.get('id', 'unknown')
            tab_title = tab.get('title', 'Без названия')
            
            analysis['tabs'][tab_id] = {
                'title': tab_title,
                'id': tab_id,
                'type': tab.get('type', 'unknown'),
                'sections': {},
                'items': [],
                'navigation': []
            }
            
            if 'items' in tab:
                analysis['tabs'][tab_id]['items'] = tab['items']
                self._analyze_tab_items_perfect(tab['items'], analysis, tab_id)
        
        return analysis
    
    def _analyze_tab_items_perfect(self, items: List, analysis: Dict, tab_id: str, path: str = ""):
        for item in items:
            item_id = item.get('id', 'unknown')
            item_title = item.get('title', 'Без названия')
            item_type = item.get('type', 'unknown')
            
            current_path = f"{path}/{item_id}" if path else item_id
            full_path = f"{tab_id}/{current_path}"
            
            element_info = {
                'id': item_id,
                'title': item_title,
                'type': item_type,
                'path': full_path,
                'tab': tab_id,
                'description': item.get('description', ''),
                'icon': item.get('icon', ''),
                'url': item.get('url', ''),
                'elements': item.get('elements', []),
                'knowledge': item.get('knowledge', {}),
                'items': []
            }
            
            if item_type == 'function':
                analysis['functions'][item_id] = element_info
            elif item_type == 'article':
                analysis['articles'][item_id] = element_info
            elif 'prayer' in item_type or any(word in item_title.lower() for word in ['prayer', 'fard', 'sunnah', 'witr']):
                analysis['prayers'][item_id] = element_info
            elif 'setting' in item_type or 'settings' in item_id:
                analysis['settings'][item_id] = element_info
            else:
                analysis['ui_elements'][item_id] = element_info
            
            keywords = self._extract_keywords_perfect(item_title, item.get('description', ''))
            for keyword in keywords:
                analysis['search_index'][keyword].append(element_info)
            
            if 'items' in item and item['items']:
                element_info['items'] = []
                for sub_item in item['items']:
                    sub_info = {
                        'id': sub_item.get('id', 'unknown'),
                        'title': sub_item.get('title', 'Без названия'),
                        'type': sub_item.get('type', 'unknown'),
                        'description': sub_item.get('description', ''),
                        'icon': sub_item.get('icon', ''),
                        'url': sub_item.get('url', ''),
                        'elements': sub_item.get('elements', [])
                    }
                    element_info['items'].append(sub_info)
                    
                    sub_keywords = self._extract_keywords_perfect(sub_info['title'], sub_info['description'])
                    for keyword in sub_keywords:
                        analysis['search_index'][keyword].append(sub_info)
                
                self._analyze_tab_items_perfect(item['items'], analysis, tab_id, current_path)
    
    def _extract_keywords_perfect(self, title: str, description: str) -> List[str]:
        text = f"{title} {description}".lower()
        keywords = []
        
        keyword_patterns = [
            'prayer', 'молитва', 'намаз', 'fard', 'sunnah', 'witr', 'tahajjud',
            'settings', 'настройки', 'app', 'приложение', 'language', 'язык',
            'dark', 'темный', 'mode', 'режим', 'notification', 'уведомления',
            'time', 'время', 'calculation', 'расчет', 'qibla', 'кибла',
            'quran', 'коран', 'article', 'статья', 'function', 'функция',
            'tab', 'вкладка', 'section', 'раздел', 'list', 'список'
        ]
        
        for pattern in keyword_patterns:
            if pattern in text:
                keywords.append(pattern)
        
        words = text.split()
        for word in words:
            if len(word) > 3 and word not in keywords:
                keywords.append(word)
        
        return keywords
    
    def _find_exact_path(self, question: str) -> Optional[Dict]:
        question_lower = question.lower()
        
        for keyword, elements in self.perfect_analysis['search_index'].items():
            if keyword in question_lower:
                for element in elements:
                    if self._is_relevant(element, question_lower):
                        return element
        
        return None
    
    def _is_relevant(self, element: Dict, question: str) -> bool:
        title = element.get('title', '').lower()
        description = element.get('description', '').lower()
        
        if any(word in title for word in question.split()):
            return True
        
        synonyms = {
            'dark': ['темный', 'темная', 'темное', 'dark mode', 'темный режим'],
            'language': ['язык', 'language', 'lang'],
            'settings': ['настройки', 'settings', 'config'],
            'prayer': ['молитва', 'намаз', 'prayer'],
            'time': ['время', 'time', 'часы']
        }
        
        for key, syn_list in synonyms.items():
            if key in question or any(syn in question for syn in syn_list):
                if any(syn in title or syn in description for syn in syn_list):
                    return True
        
        return False
    
    def _create_perfect_system_message(self, question: str, found_element: Optional[Dict]) -> str:
        
        base_message = """Ты - эксперт по приложению NamazApp. Ты знаешь ВСЮ структуру приложения до мельчайших деталей.

ПОЛНАЯ СТРУКТУРА ПРИЛОЖЕНИЯ ИЗ app_structure.json:
"""
        
        base_message += "\n📱 ВКЛАДКИ ПРИЛОЖЕНИЯ:\n"
        for tab_id, tab_info in self.perfect_analysis['tabs'].items():
            base_message += f"\nВКЛАДКА: {tab_info['title']} (ID: {tab_id}, Тип: {tab_info['type']})\n"
            
            if 'items' in tab_info:
                base_message += "ЭЛЕМЕНТЫ ВКЛАДКИ:\n"
                for item in tab_info['items']:
                    base_message += f"  - {item.get('title', 'Без названия')} (ID: {item.get('id', 'unknown')}, Тип: {item.get('type', 'unknown')})\n"
                    if item.get('description'):
                        base_message += f"    Описание: {item['description']}\n"
                    if item.get('icon'):
                        base_message += f"    Иконка: {item['icon']}\n"
                    if item.get('url'):
                        base_message += f"    URL: {item['url']}\n"
                    if item.get('elements'):
                        base_message += f"    Элементы: {item['elements']}\n"
                    if item.get('knowledge'):
                        base_message += f"    Знания: {item['knowledge']}\n"
                    if item.get('shows'):
                        base_message += f"    Показывается: {item['shows']}\n"
                    
                    if item.get('items'):
                        base_message += f"    ПОДЭЛЕМЕНТЫ:\n"
                        for sub_item in item['items']:
                            base_message += f"      - {sub_item.get('title', 'Без названия')} (ID: {sub_item.get('id', 'unknown')}, Тип: {sub_item.get('type', 'unknown')})\n"
                            if sub_item.get('description'):
                                base_message += f"        Описание: {sub_item['description']}\n"
                            if sub_item.get('icon'):
                                base_message += f"        Иконка: {sub_item['icon']}\n"
                            if sub_item.get('url'):
                                base_message += f"        URL: {sub_item['url']}\n"
                            if sub_item.get('elements'):
                                base_message += f"        Элементы: {sub_item['elements']}\n"
                            if sub_item.get('knowledge'):
                                base_message += f"        Знания: {sub_item['knowledge']}\n"
                            
                            if sub_item.get('items'):
                                base_message += f"        ЭЛЕМЕНТЫ:\n"
                                for sub_sub_item in sub_item['items']:
                                    base_message += f"          - {sub_sub_item.get('title', 'Без названия')} (ID: {sub_sub_item.get('id', 'unknown')}, Тип: {sub_sub_item.get('type', 'unknown')})\n"
                                    if sub_sub_item.get('description'):
                                        base_message += f"            Описание: {sub_sub_item['description']}\n"
                                    if sub_sub_item.get('icon'):
                                        base_message += f"            Иконка: {sub_sub_item['icon']}\n"
                                    if sub_sub_item.get('url'):
                                        base_message += f"            URL: {sub_sub_item['url']}\n"
                                    if sub_sub_item.get('elements'):
                                        base_message += f"            Элементы: {sub_sub_item['elements']}\n"
                                    if sub_sub_item.get('knowledge'):
                                        base_message += f"            Знания: {sub_sub_item['knowledge']}\n"
        
        base_message += "\n🕌 МОЛИТВЫ (ТОЧНЫЕ ДАННЫЕ):\n"
        for prayer_id, prayer_info in self.perfect_analysis['prayers'].items():
            base_message += f"- {prayer_info['title']} (ID: {prayer_id})\n"
            base_message += f"  Тип: {prayer_info['type']}\n"
            base_message += f"  Путь: {prayer_info['path']}\n"
            base_message += f"  Вкладка: {prayer_info['tab']}\n"
            if prayer_info.get('description'):
                base_message += f"  Описание: {prayer_info['description']}\n"
            if prayer_info.get('icon'):
                base_message += f"  Иконка: {prayer_info['icon']}\n"
            if prayer_info.get('knowledge'):
                base_message += f"  Знания: {prayer_info['knowledge']}\n"
        
        base_message += "\n⚙️ НАСТРОЙКИ (ТОЧНЫЕ ДАННЫЕ):\n"
        for setting_id, setting_info in self.perfect_analysis['settings'].items():
            base_message += f"- {setting_info['title']} (ID: {setting_id})\n"
            base_message += f"  Тип: {setting_info['type']}\n"
            base_message += f"  Путь: {setting_info['path']}\n"
            base_message += f"  Вкладка: {setting_info['tab']}\n"
            if setting_info.get('description'):
                base_message += f"  Описание: {setting_info['description']}\n"
            if setting_info.get('elements'):
                base_message += f"  Элементы: {setting_info['elements']}\n"
            if setting_info.get('knowledge'):
                base_message += f"  Знания: {setting_info['knowledge']}\n"
        
        base_message += "\n📚 СТАТЬИ (ТОЧНЫЕ ДАННЫЕ):\n"
        for article_id, article_info in self.perfect_analysis['articles'].items():
            base_message += f"- {article_info['title']} (ID: {article_id})\n"
            base_message += f"  Тип: {article_info['type']}\n"
            base_message += f"  Путь: {article_info['path']}\n"
            base_message += f"  Вкладка: {article_info['tab']}\n"
            if article_info.get('description'):
                base_message += f"  Описание: {article_info['description']}\n"
            if article_info.get('url'):
                base_message += f"  URL: {article_info['url']}\n"
            if article_info.get('icon'):
                base_message += f"  Иконка: {article_info['icon']}\n"
        
        base_message += "\n🔧 ФУНКЦИИ (ТОЧНЫЕ ДАННЫЕ):\n"
        for func_id, func_info in self.perfect_analysis['functions'].items():
            base_message += f"- {func_info['title']} (ID: {func_id})\n"
            base_message += f"  Тип: {func_info['type']}\n"
            base_message += f"  Путь: {func_info['path']}\n"
            base_message += f"  Вкладка: {func_info['tab']}\n"
            if func_info.get('description'):
                base_message += f"  Описание: {func_info['description']}\n"
            if func_info.get('url'):
                base_message += f"  URL: {func_info['url']}\n"
            if func_info.get('icon'):
                base_message += f"  Иконка: {func_info['icon']}\n"
        
        base_message += "\n🎨 UI ЭЛЕМЕНТЫ (ТОЧНЫЕ ДАННЫЕ):\n"
        for ui_id, ui_info in self.perfect_analysis['ui_elements'].items():
            base_message += f"- {ui_info['title']} (ID: {ui_id})\n"
            base_message += f"  Тип: {ui_info['type']}\n"
            base_message += f"  Путь: {ui_info['path']}\n"
            base_message += f"  Вкладка: {ui_info['tab']}\n"
            if ui_info.get('description'):
                base_message += f"  Описание: {ui_info['description']}\n"
            if ui_info.get('icon'):
                base_message += f"  Иконка: {ui_info['icon']}\n"
            if ui_info.get('url'):
                base_message += f"  URL: {ui_info['url']}\n"
            if ui_info.get('elements'):
                base_message += f"  Элементы: {ui_info['elements']}\n"
            if ui_info.get('knowledge'):
                base_message += f"  Знания: {ui_info['knowledge']}\n"
        
        if found_element:
            base_message += f"""
🎯 НАЙДЕННЫЙ ЭЛЕМЕНТ ДЛЯ ВОПРОСА:
- Название: {found_element.get('title', 'Неизвестно')}
- ID: {found_element.get('id', 'Неизвестно')}
- Тип: {found_element.get('type', 'Неизвестно')}
- Путь: {found_element.get('path', 'Неизвестно')}
- Вкладка: {found_element.get('tab', 'Неизвестно')}
- Описание: {found_element.get('description', 'Нет описания')}
- Иконка: {found_element.get('icon', 'Нет иконки')}
- URL: {found_element.get('url', 'Нет URL')}
- Элементы: {found_element.get('elements', [])}
- Знания: {found_element.get('knowledge', {})}
"""
            
            if found_element.get('items'):
                base_message += "\nПОДЭЛЕМЕНТЫ НАЙДЕННОГО ЭЛЕМЕНТА:\n"
                for item in found_element['items']:
                    base_message += f"- {item.get('title', 'Без названия')} (ID: {item.get('id', 'unknown')}, Тип: {item.get('type', 'unknown')})\n"
                    if item.get('description'):
                        base_message += f"  Описание: {item['description']}\n"
                    if item.get('icon'):
                        base_message += f"  Иконка: {item['icon']}\n"
                    if item.get('url'):
                        base_message += f"  URL: {item['url']}\n"
                    if item.get('elements'):
                        base_message += f"  Элементы: {item['elements']}\n"
                    if item.get('knowledge'):
                        base_message += f"  Знания: {item['knowledge']}\n"
        
        base_message += f"""
📊 СТАТИСТИКА:
- Всего вкладок: {len(self.perfect_analysis['tabs'])}
- Всего функций: {len(self.perfect_analysis['functions'])}
- Всего статей: {len(self.perfect_analysis['articles'])}
- Всего молитв: {len(self.perfect_analysis['prayers'])}
- Всего настроек: {len(self.perfect_analysis['settings'])}
- Всего UI элементов: {len(self.perfect_analysis['ui_elements'])}

ПРАВИЛА ОТВЕТОВ:
1. Отвечай ТОЛЬКО на основе предоставленной структуры приложения
2. Используй ТОЧНЫЕ ID, названия и пути из структуры
3. Указывай ТОЧНЫЙ путь навигации с ID элементов
4. Объясняй каждый шаг навигации
5. Если элемент не найден - говори об этом
6. Используй Markdown форматирование
7. Будь максимально точным и полезным
8. Всегда указывай ID элементов в ответе
9. Используй ТОЧНЫЕ названия из структуры

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {question}

ОТВЕЧАЙ МАКСИМАЛЬНО ТОЧНО НА ОСНОВЕ ВСЕЙ ПРЕДОСТАВЛЕННОЙ СТРУКТУРЫ ПРИЛОЖЕНИЯ!"""
        
        return base_message
    
    async def generate_perfect_response(self, context: str) -> str:
        try:
            # Для поиска элемента используем только последний вопрос из контекста
            last_question = context.split('🎯 ТЕКУЩИЙ ВОПРОС:')[-1].split('\n')[0].strip() if '🎯 ТЕКУЩИЙ ВОПРОС:' in context else context
            found_element = self._find_exact_path(last_question)
            
            system_message = self._create_perfect_system_message(last_question, found_element)
            
            payload = {
                "user_id": "multi_agent_recommender",
                "user_message": context,  # Передаем весь контекст!
                "system_message": system_message,
                "llm_model": "gemini-2.0-flash",
                "response_schema": {
                    "answer": "str"
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "answer" in result:
                    answer = result["answer"]
                    
                    formatted_response = self._format_perfect_response(answer, found_element, last_question)
                    return formatted_response
                else:
                    return "❌ Ошибка: Неожиданный формат ответа от API"
            else:
                return f"❌ Ошибка API: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return f"❌ Ошибка: {str(e)}"
    
    def _format_perfect_response(self, api_answer: str, found_element: Optional[Dict], question: str) -> str:
        response_parts = []
        
        response_parts.append(api_answer)
        
        if found_element:
            response_parts.append(f"\n\n🎯 **ТОЧНОСТЬ:**")
            response_parts.append(f"Найден элемент: **{found_element.get('title', 'Неизвестно')}**")
            response_parts.append(f"Путь: `{found_element.get('path', 'Неизвестно')}`")
            response_parts.append(f"Тип: {found_element.get('type', 'Неизвестно')}")
        else:
            response_parts.append(f"\n\n⚠️ **ТОЧНОСТЬ:**")
            response_parts.append("Элемент не найден в структуре приложения")
            response_parts.append("Ответ основан на общих знаниях о приложении")
        
        return "\n".join(response_parts)

def main():
    print("🎯 ТЕСТИРОВАНИЕ МАКСИМАЛЬНО ТОЧНОГО GPT CLIENT")
    print("=" * 60)
    
    client = PerfectGPTClient()
    
    test_questions_list = [
        "Как включить темный режим?",
        "Где найти настройки языка?",
        "Как изменить время молитв?",
        "Где найти киблу?",
        "Что такое фард молитвы?",
        "Как записать свой голос?"
    ]
    
    print("\n🤖 ТЕСТИРОВАНИЕ ТОЧНЫХ ОТВЕТОВ:")
    print("=" * 60)
    
    async def test_questions():
        for i, question in enumerate(test_questions_list, 1):
            print(f"\n{i}. Вопрос: {question}")
            print("-" * 50)
            try:
                # Формируем контекст для теста (эмулируем историю)
                context = f"ВОПРОС ПОЛЬЗОВАТЕЛЯ: {question}"
                response = await client.generate_perfect_response(context)
                print(f"Ответ:\n{response}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            print("-" * 50)
    asyncio.run(test_questions())
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)

if __name__ == "__main__":
    main() 
