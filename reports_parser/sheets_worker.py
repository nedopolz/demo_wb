import datetime
import os
import re
import time

import aiohttp
import gspread
from aiohttp import ClientTimeout
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from loguru import logger
from reports_parser.config import SHEET_URL, TEMPLATE_LIST_NAME, INFO_LIST_NAME, PHOTO_URL, DOCS_PATH, \
    PROJECT_ID, PRIVATE_KEY_ID, PRIVATE_KEY, CLIENT_EMAIL, CLIENT_ID, AUTH_URI, TOKEN_URI, AUTH_PROVIDER_X509_CERT_URL, \
    CLIENT_X509_CERT_URL
from reports_parser.utils import number_to_month

akk_dict = {
    "type": "service_account",
    "project_id": PROJECT_ID,
    "private_key_id": PRIVATE_KEY_ID,
    "private_key": PRIVATE_KEY.replace('\\n', '\n'),
    "client_email": CLIENT_EMAIL,
    "client_id": CLIENT_ID,
    "auth_uri": AUTH_URI,
    "token_uri": TOKEN_URI,
    "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": CLIENT_X509_CERT_URL
}

logger.debug(akk_dict)

class SheetWorker:
    """
    class for google sheets uploads
    """

    def __init__(self) -> None:
        """creates connection, and connects to spreadsheet"""
        # self.gc = gspread.service_account(secret_payload)
        self.gc = gspread.service_account_from_dict(akk_dict)
        try:
            self.sheet = self.gc.open_by_url(SHEET_URL)
        except gspread.exceptions.NoValidUrlKeyFound:
            print('invalid url')  # TODO add logs

    def is_list_exsist(self, list_name: str) -> bool:
        """checks if list exists"""
        try:
            self.sheet.worksheet(title=list_name)
            return True
        except gspread.exceptions.WorksheetNotFound:
            return False

    def paste_csv(self, csvFile, sheet, cell, delimetr):
        if '!' in cell:
            (tabName, cell) = cell.split('!')
            wks = sheet.worksheet(tabName)
        else:
            wks = sheet.sheet1
        (firstRow, firstColumn) = gspread.utils.a1_to_rowcol(cell)

        with open(csvFile, 'r') as f:
            csvContents = f.read()

        body = {
            'requests': [{
                'pasteData': {
                    "coordinate": {
                        "sheetId": wks.id,
                        "rowIndex": firstRow - 1,
                        "columnIndex": firstColumn - 1,
                    },
                    "data": csvContents,
                    "type": 'PASTE_VALUES',
                    "delimiter": f'{delimetr}',
                }
            }]
        }
        return sheet.batch_update(body)

    def data_list_creation(self, month_name: str) -> None:
        """creates worksheet to insert data"""
        self.sheet.add_worksheet(title=f'{month_name}-data', rows=1, cols=1)  # TODO name

    def main_list_creation(self, month_name: str) -> None:
        """copy report list teamplate"""
        worksheet = self.sheet.worksheet(title=TEMPLATE_LIST_NAME)
        self.sheet.duplicate_sheet(source_sheet_id=worksheet.id, new_sheet_name=f'{month_name}-wb')  # TODO name
        worksheet = self.sheet.worksheet(title=f'{month_name}-wb')

    def next_available_row(self, worksheet, col_number) -> str:
        """gets next clear row number"""
        return str(len(worksheet.col_values(col_number)) + 1)

    def extend_remains(self, month_name: str, path_to_csv: str) -> None:
        """extends remains for given mount"""
        worksheet = self.sheet.worksheet(title=f'{month_name}-wb')
        worksheet.add_rows(10)
        next_row = self.next_available_row(worksheet, 23)  # TODO path
        if int(next_row) < 4:  # TODO path
            next_row = 4  # TODO path
        self.paste_csv(csvFile=path_to_csv, sheet=self.sheet, cell=f'{month_name}-wb!V{next_row}',
                       delimetr=',')  # TODO path

    def extend_report(self, month_name: str, path_to_csv: str) -> None:
        """extends remains for given mount"""
        worksheet = self.sheet.worksheet(title=f'{month_name}-wb')
        worksheet.add_rows(10)
        next_row = self.next_available_row(worksheet, 1)  # TODO path
        if int(next_row) < 4:  # TODO path
            next_row = 4  # TODO path
        self.paste_csv(csvFile=path_to_csv, sheet=self.sheet, cell=f'{month_name}-wb!A{next_row}', delimetr=';')

    def clear_remains(self, month_name: str) -> None:
        worksheet = self.sheet.worksheet(f'{month_name}-wb')
        last_row = self.next_available_row(worksheet, 23)  # TODO path
        worksheet.batch_clear([f'V4:X{last_row}'])

    async def parse_name_photo_2(self, product_id: int) -> [str, str]:
        url = PHOTO_URL.format(product_id)
        name = '-'
        photo = '-'
        async with aiohttp.request(method='get', url=url, timeout=ClientTimeout(60)) as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            name = soup.findAll("span", {"data-link": "text{:productCard^goodsName}"})
            name = re.findall(r'^.+>(.+)<.+$', str(name))
            images = soup.findAll('img')
            image = str(images[1]).replace('\n', '1')
            link = re.findall(r'^.+src=\"(.+)\".+$', image)
            name = name[0]
            photo = f'https:{link[0]}'.replace('/tm/', '/big/')
            time.sleep(6)
        return name, photo

    def create_product_name(self, month_name):
        """creates product name and main photo url colums"""
        worksheet = self.sheet.worksheet(title=f'{month_name}-wb')
        row = 4  # TODO path
        while True:
            product_id = worksheet.get(f'D{row}')  # TODO path
            if not product_id:
                break
            product_id = product_id[0][0]
            name, photo_link = async_to_sync(self.parse_name_photo_2)(product_id)
            worksheet.update(f'E{row}:L{row}', [[photo_link, name]])  # TODO path
            row += 1

    def add_parsings_datetime(self):
        worksheet = self.sheet.worksheet(title=INFO_LIST_NAME)
        today = datetime.datetime.today()
        today = f'{today.day}.{today.month}.{today.year} {today.hour}:{today.minute}'
        worksheet.update('A1', today)

    def month_initer(self) -> bool:
        """checks if month needs creation, and create it if needed"""
        date = datetime.date.today()
        month = date.month
        month = number_to_month(month)
        main_list_exist = self.is_list_exsist(f'{month}-wb')  # TODO name
        if not main_list_exist:
            self.main_list_creation(month)
        else:
            return False

    def do_everything(self):
        new_month = self.month_initer()
        report_path = f'{DOCS_PATH}/{datetime.date.today()}.csv'
        mounth = number_to_month(datetime.date.today().month)
        self.extend_report(month_name=mounth, path_to_csv=report_path)
        files = [x[0] for x in os.walk(f'{DOCS_PATH}')]  # TODO path
        files.pop(0)
        files = [f'{i}/remain.csv' for i in files]  # TODO path
        self.clear_remains(mounth)
        for file in files:
            self.extend_remains(month_name=mounth, path_to_csv=file)
        self.create_product_name(month_name=mounth)

