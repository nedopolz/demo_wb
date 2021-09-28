import datetime
from reports_parser.db.database import Session
from reports_parser.db.models.account import ReportAccount

def number_to_month(number: int) -> str:
    """converts month number to date"""
    if number == 1:
        return "Январь"
    elif number == 2:
        return "Февраль"
    elif number == 3:
        return "Март"
    elif number == 4:
        return "Апрель"
    elif number == 5:
        return "Май"
    elif number == 6:
        return "Июнь"
    elif number == 7:
        return "Июль"
    elif number == 8:
        return "Август"
    elif number == 9:
        return "Сентябрь"
    elif number == 10:
        return "Октябрь"
    elif number == 11:
        return "Ноябрь"
    elif number == 12:
        return "Декабрь"

def monday_date(curent_date: datetime):
    """returns next monday date"""
    next_monday = curent_date + datetime.timedelta(days=-curent_date.weekday(), weeks=1)
    return next_monday

async def setter_false_for_parsing():
    async with Session.begin() as session:
        accounts = await ReportAccount.get_all(session)
        for akk in accounts:
            await akk.update_remains_status(session, akk.id, status=False)
            await akk.update_report_status(session, akk.id, status=False)

async def check_if_parsing_needed():
    async with Session.begin() as session:
        parsing_need = await ReportAccount.check_for_parsing_need(session)
    return parsing_need

async def get_name(newID:str):
    async with Session.begin() as session:
        name = await ReportAccount.get_name(session, newID)
    return name

def get_prev_monday():
    curent_date = datetime.date.today()
    next_monday = curent_date + datetime.timedelta(days=-curent_date.weekday(), weeks=1)
    return next_monday - datetime.timedelta(days=7)
