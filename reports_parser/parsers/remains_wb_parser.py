import asyncio

from loguru import logger

from reports_parser.db.database import Session
from reports_parser.db.models import ReportPhoneAccount, ReportAccount
from reports_parser.parsers.wildberries import WildberriesParser


async def remains_parser():
    """
    загружает отчеты в соответсвующие папки
    """
    logger.debug('Feedback start parsing.')

    async with Session.begin() as session:
        accounts = await ReportPhoneAccount.get_all(session)

    for account in accounts:
        parser = WildberriesParser(account)
        await parser.check_login()
        if not parser.is_logined():
            logger.error("LOGIN - FAILED")
            break
        if account.wait_code:
            logger.error("WAIT CODE!!! DONT START PARSER!")
            break

        async with Session.begin() as session:
            supply_accounts = await ReportAccount.get_supply_accounts(account.id, session)

        for sup_acc in supply_accounts:
            if sup_acc.parsed_report and sup_acc.parsed_remains:
                continue
            if not sup_acc.parsed_remains and sup_acc.parsed_report:
                try:
                    logger.debug(f'\nTRY parse remains\n')
                    await parser.set_supply_account_id(sup_acc.newID)
                    await parser.get_remains(sup_acc)
                    continue
                except Exception as e:
                    logger.error(f'\n\nERROR {e=}\n\n')
                    continue
            try:
                logger.debug(f'\nTRY parse reports and remains\n')
                await asyncio.sleep(2)
                parser.set_supply_account_id(sup_acc.newID)
                await parser.get_report(sup_acc)
                await parser.get_remains(sup_acc)
            except Exception as e:
                logger.error(f'\n\nERROR {e=}\n\n')
                logger.debug(f'\n\nWAIT 60 SECONDS!!!\n\n')
                await asyncio.sleep(60)
            else:
                logger.debug('reports and remains parsed successfully.')

        await parser.close()
    return True
