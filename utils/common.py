from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


async def generate_excel(data):
    if not data:
        return None

    with BytesIO() as excel_buffer:
        workbook = Workbook()
        sheet = workbook.active

        sheet.append([
            "Дата", "ФИО", "Юзернейм", "Мастер", "Услуга", "Пожелания"
        ])

        for cell in sheet["1:1"]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        for user in data:
            sheet.append([
                *user
            ])

        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column].width = adjusted_width

        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        return excel_buffer.getvalue()
