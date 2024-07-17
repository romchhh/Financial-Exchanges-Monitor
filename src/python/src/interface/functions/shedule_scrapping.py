import datetime
import pytz
import os
import glob
from main import bot, dp
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from interface.data.config import logs

async def send_report():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    kyiv_time = datetime.datetime.now(kyiv_tz)
    await bot.send_message(logs, f'Привіт! Запуск спайдеру о {kyiv_time.strftime("%H:%M:%S")}')

    process = CrawlerProcess(get_project_settings())
    process.crawl('pinksale')
    process.start()

    # Send the latest exported CSV file to the logs
    await send_latest_exported_file()

async def send_latest_exported_file():
    EXPORT_PATH = r'C:\Projects\TeleBots\pinksale-launchpad-tracker-main\src\storage\export'
    files = sorted(glob.glob(os.path.join(EXPORT_PATH, '*.csv')), key=os.path.getmtime, reverse=True)
    
    if files:
        latest_file = files[0]
        with open(latest_file, 'rb') as file:
            await bot.send_document(logs, file, caption="Експортований CSV файл.")
    else:
        await bot.send_message(logs, "Не знайдено жодного експортованого файлу.")
