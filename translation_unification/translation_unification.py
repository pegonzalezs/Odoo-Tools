# click-odoo -d fsch_test -c /etc/odoo-server.conf 
# --logfile=/var/log/odoo/unitranslationlog.log ./translation_unification.py
# --exportTranslations --user-id 0000 --model-id 1111 --field_id 2222
#
import openpyxl
from openpyxl import Workbook

import argparse
import logging
import sys

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
_logger.addHandler(ch)

class TranslationUnification(object):
    def __init__(self, sysArgs):
        self.args = argparse.ArgumentParser()
        self.args.add_argument(
            '-e',
            '--exportTranslations',
            action='store',
            required=True,
            help='Export or import mode'
        )
        self.args.add_argument(
            '-i',
            '--importTranslations',
            action='store',
            required=True,
            help='Export or import mode'
        )
        self.args.add_argument(
            '-uid',
            '--user-id',
            type=int,
            required=True,
            help='User ID representing the language'
        )
        self.args.add_argument(
            '-mid',
            '--model-id',
            type=str,
            required=True,
            help='ID of the model for translation'
        )
        self.args.add_argument(
            '-fid',
            '--field-id',
            type=str,
            required=True,
            help='ID of the field to translate'
        )
        self.args = self.args.parse_args()


    def export_translations(self):
        # Initialize an empty dictionary to store translation data
        translation_data = {}

        # Log in as the user with the specified language preference
        user = self.env['res.users'].browse(self.args.user_id)
        lang_code = user.lang or 'en_US'  # Default to English if no language is set

        # Set the language context for the user
        with self.env.user.change_lang(lang_code):
            # Query records for the specified model and field
            records = self.env[self.args.model_id].search([])

            # Collect translation data for each record
            for record in records:
                translation_value = record[self.args.field_id]

                # Store translation data in the dictionary
                translation_data.setdefault(record.id, {})[lang_code] = translation_value

        # Export `translation_data` to an Excel file using openpyxl
        wb = Workbook()
        ws = wb.active

        # Create headers for the Excel sheet
        headers = ['Record ID'] + [lang_code]
        ws.append(headers)

        # Add translation data to the Excel sheet
        for record_id, translations in translation_data.items():
            row_data = [record_id] + [translations.get(lang_code, '')]
            ws.append(row_data)

        # Save the Excel file
        wb.save('translations.xlsx')

        logging.info("Translations exported successfully. File saved as 'translations.xlsx'")

    def import_translations(self):
        # Import translations from Excel

        wb = openpyxl.load_workbook('translations.xlsx')
        sheet = wb.active

        # Log in as the user with the specified language preference
        user = self.env['res.users'].browse(self.args.user_id)
        lang_code = user.lang or 'en_US'  # Default to English if no language is set

        # Iterate through rows in the Excel sheet
        for row in sheet.iter_rows(min_row=2, values_only=True):
            record_id, translation_value = row

            # Set the language context for the user
            with self.env.user.change_lang(lang_code):
                # Update the translation for the specified record and field
                record = self.env[self.args.model_id].browse(record_id)
                record[self.args.field_id] = translation_value

        # Commit the changes
        self._cr.commit()

        logging.info("Translations imported successfully")

    def run(self):
        if self.args.mode == 'export':
            self.export_translations()
        elif self.args.mode == 'import':
            self.import_translations()
        else:
            logging.error("Invalid mode. Use 'export' or 'import'.")

if __name__ == '__main__':
    translationuni = TranslationUnification(sys.argv[1:])
    if translationuni.args.exportTranslations:
        file = translationuni.args.duplicates and translationuni.args.duplicates[0]
        translationuni.export_translations()
    if translationuni.args.importTranslations:
        file = translationuni.args.sort and translationuni.args.sort[0]
        translationuni.import_translations()
