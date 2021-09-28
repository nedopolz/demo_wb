import asyncio
from asgiref.sync import sync_to_async

from loguru import logger

from reports_parser.db.database import setup_db
from reports_parser.logger import setup_logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reports_parser.parsers.remains_wb_parser import remains_parser
from reports_parser.utils import check_if_parsing_needed, setter_false_for_parsing
from reports_parser.sheets_worker import SheetWorker
from reports_parser.data_former import ReportFormer

SheetWorker = SheetWorker()
ReportFormer = ReportFormer()


async def on_startup():
    await setup_db()


async def parse():
    while True:
        logger.debug(f'\n\nnew try\n\n')
        parsed = await remains_parser()
        if not await check_if_parsing_needed() and parsed:
            logger.debug(f'\n\nParsed\n\n')
            break
        else:
            await sync_to_async(SheetWorker.add_parsings_datetime)()
            logger.debug(f'\n\nwait 1 hour\n\n')
            await asyncio.sleep(3600)
    if parsed:
        await sync_to_async(ReportFormer.start_convert)()
        await sync_to_async(SheetWorker.do_everything)()
        await setter_false_for_parsing()


if __name__ == '__main__':
    setup_logger("DEBUG")
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()
#     scheduler.add_job(parse, 'cron', day_of_week=0, id='remains_parser_task', replace_existing=True)

    try:
        loop.run_until_complete(on_startup())
        loop.run_until_complete(parse())
        loop.run_forever()
    except KeyboardInterrupt as e:
        logger.debug(f'\n\nLOOP ERROR{e}\n\n')
        pass
    finally:
        loop.close()
        logger.debug(f'\n\nShutdown finally\n\n')
