import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from perfect_gpt_client import PerfectGPTClient

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, mongo_uri: str):
        """
        Инициализация менеджера диалогов
        
        Args:
            mongo_uri: URI для подключения к MongoDB
        """
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.swp_db
        self.conversations_collection = self.db.conversations
        self.perfect_client = PerfectGPTClient()
        
    async def get_user_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Получает историю диалогов пользователя
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество последних сообщений
            
        Returns:
            Список сообщений пользователя
        """
        try:
            # Получаем все диалоги пользователя
            cursor = self.conversations_collection.find({"user_id": user_id})
            conversations = await cursor.to_list(length=100)
            
            if not conversations:
                return []
            
            # Собираем все сообщения из всех диалогов
            all_messages = []
            for conv in conversations:
                if 'messages' in conv:
                    all_messages.extend(conv['messages'])
            
            # Сортируем по времени и берем последние limit сообщений
            all_messages.sort(key=lambda x: x.get('time', datetime.min))
            return all_messages[-limit:] if len(all_messages) > limit else all_messages
            
        except Exception as e:
            logger.error(f"Ошибка получения истории диалогов для пользователя {user_id}: {e}")
            return []
    
    async def save_user_message(self, user_id: int, message_text: str) -> bool:
        """
        Сохраняет сообщение пользователя в БД
        
        Args:
            user_id: ID пользователя
            message_text: Текст сообщения
            
        Returns:
            True если успешно сохранено
        """
        try:
            message = {
                "sender": "user",
                "text": message_text,
                "time": datetime.utcnow()
            }
            
            # Ищем существующий диалог пользователя
            existing_conv = await self.conversations_collection.find_one({"user_id": user_id})
            
            if existing_conv:
                # Добавляем сообщение к существующему диалогу
                await self.conversations_collection.update_one(
                    {"_id": existing_conv["_id"]},
                    {"$push": {"messages": message}}
                )
            else:
                # Создаем новый диалог
                new_conv = {
                    "user_id": user_id,
                    "messages": [message]
                }
                await self.conversations_collection.insert_one(new_conv)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения пользователя {user_id}: {e}")
            return False
    
    async def save_bot_response(self, user_id: int, response_text: str) -> bool:
        """
        Сохраняет ответ бота в БД
        
        Args:
            user_id: ID пользователя
            response_text: Текст ответа бота
            
        Returns:
            True если успешно сохранено
        """
        try:
            message = {
                "sender": "bot",
                "text": response_text,
                "time": datetime.utcnow()
            }
            
            # Ищем существующий диалог пользователя
            existing_conv = await self.conversations_collection.find_one({"user_id": user_id})
            
            if existing_conv:
                # Добавляем сообщение к существующему диалогу
                await self.conversations_collection.update_one(
                    {"_id": existing_conv["_id"]},
                    {"$push": {"messages": message}}
                )
            else:
                # Создаем новый диалог
                new_conv = {
                    "user_id": user_id,
                    "messages": [message]
                }
                await self.conversations_collection.insert_one(new_conv)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения ответа бота для пользователя {user_id}: {e}")
            return False
    
    def _create_context_from_history(self, history: List[Dict], current_question: str) -> str:
        """
        Создает контекст из истории диалогов для LLM
        
        Args:
            history: История диалогов
            current_question: Текущий вопрос пользователя
            
        Returns:
            Строка с контекстом для LLM
        """
        if not history:
            return f"ВОПРОС ПОЛЬЗОВАТЕЛЯ: {current_question}"
        
        context_parts = ["📝 ИСТОРИЯ ДИАЛОГА:"]
        
        for i, message in enumerate(history[-5:], 1):  # Последние 5 сообщений
            sender = "👤 ПОЛЬЗОВАТЕЛЬ" if message.get('sender') == 'user' else "🤖 БОТ"
            text = message.get('text', '')
            time = message.get('time', '')
            
            context_parts.append(f"{i}. {sender}: {text}")
            if time:
                context_parts.append(f"   Время: {time}")
            context_parts.append("")
        
        context_parts.append(f"🎯 ТЕКУЩИЙ ВОПРОС: {current_question}")
        context_parts.append("")
        context_parts.append("💡 ИНСТРУКЦИЯ: Учитывай историю диалога при ответе. Если пользователь продолжает предыдущую тему - свяжи ответы. Если это новый вопрос - отвечай независимо.")
        
        return "\n".join(context_parts)
    
    async def generate_contextual_response(self, user_id: int, question: str) -> str:
        """
        Генерирует ответ с учетом истории диалогов пользователя
        
        Args:
            user_id: ID пользователя
            question: Вопрос пользователя
            
        Returns:
            Ответ LLM с учетом контекста
        """
        try:
            # Сохраняем вопрос пользователя
            await self.save_user_message(user_id, question)
            
            # Получаем историю диалогов
            history = await self.get_user_conversation_history(user_id, limit=10)
            
            # Создаем контекст из истории
            context = self._create_context_from_history(history, question)
            
            # Генерируем ответ с помощью PerfectGPTClient, передавая весь контекст!
            response = await self.perfect_client.generate_perfect_response(context)
            
            # Добавляем контекстную информацию к ответу
            contextual_response = f"{response}\n\n📚 *Контекст диалога учтен*"
            
            # Сохраняем ответ бота
            await self.save_bot_response(user_id, contextual_response)
            
            return contextual_response
            
        except Exception as e:
            logger.error(f"Ошибка генерации контекстного ответа для пользователя {user_id}: {e}")
            return f"❌ Извините, произошла ошибка при обработке вашего вопроса: {str(e)}"
    
    async def clear_user_history(self, user_id: int) -> bool:
        """
        Очищает историю диалогов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если успешно очищено
        """
        try:
            result = await self.conversations_collection.delete_many({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Ошибка очистки истории для пользователя {user_id}: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """
        Получает статистику пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь со статистикой
        """
        try:
            conversations = await self.conversations_collection.find({"user_id": user_id}).to_list(length=100)
            
            total_messages = 0
            user_messages = 0
            bot_messages = 0
            
            for conv in conversations:
                if 'messages' in conv:
                    total_messages += len(conv['messages'])
                    for msg in conv['messages']:
                        if msg.get('sender') == 'user':
                            user_messages += 1
                        elif msg.get('sender') == 'bot':
                            bot_messages += 1
            
            return {
                "total_conversations": len(conversations),
                "total_messages": total_messages,
                "user_messages": user_messages,
                "bot_messages": bot_messages
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики для пользователя {user_id}: {e}")
            return {}

# Пример использования
async def main():
    # Инициализация менеджера (замените на ваш MONGO_URI)
    manager = ConversationManager("your_mongo_uri_here")
    
    # Пример генерации ответа с контекстом
    user_id = 123456789
    question = "Как изменить язык приложения?"
    
    response = await manager.generate_contextual_response(user_id, question)
    print(f"Ответ: {response}")
    
    # Получение статистики
    stats = await manager.get_user_stats(user_id)
    print(f"Статистика: {stats}")

if __name__ == "__main__":
    asyncio.run(main()) 
