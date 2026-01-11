import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """Доступные команды:
                     
/start - начать работу с ботом и получить приветственное сообщение.
/help - получить список доступных команд.
/show_city <city_name> - отобразить указанный город на карте.
/remember_city <city_name> - сохранить город в список избранных.
/show_my_cities - показать все сохраненные города.""")
    # Допиши команды бота

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите название города после команды.\nНапример: /show_city Moscow")
            return
            
        city_name = ' '.join(parts[1:])
        
        cities = [city_name]
        if manager.create_graph(cities, 'city_map.png'):
            with open('city_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f"Город: {city_name}")
        else:
            bot.send_message(message.chat.id, f"Не удалось найти город '{city_name}'. Убедитесь, что название написано на английском.")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите название города после команды.\nНапример: /remember_city Moscow")
            return
            
        city_name = ' '.join(parts[1:])
        
        if manager.add_city(user_id, city_name):
            bot.send_message(message.chat.id, f'Город "{city_name}" успешно сохранен!')
        else:
            bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении города: {str(e)}")

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    try:
        cities = manager.select_cities(message.chat.id)
        if not cities:
            bot.send_message(message.chat.id, 'У вас пока нет сохраненных городов. Используйте /remember_city [город] чтобы добавить.')
            return
            
        cities_list = "\n".join([f"• {city}" for city in cities])
        bot.send_message(message.chat.id, f"Ваши сохраненные города:\n{cities_list}")
        
        if manager.create_graph(cities, 'my_cities_map.png'):
            with open('my_cities_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="Ваши сохраненные города на карте")
        else:
            bot.send_message(message.chat.id, 'Не получилось отрисовать карту с вашими городами.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    bot.polling(none_stop=True)