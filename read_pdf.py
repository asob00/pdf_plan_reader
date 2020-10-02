import tabula
import json


def read_pdf():
    pdf_file = "/home/adam/Pulpit/20-21-cs1-sem3.pdf"
    table = tabula.read_pdf(pdf_file, pages=1, output_format="json")[0]['data']
    table += tabula.read_pdf(pdf_file, pages=2, output_format="json")[0]['data']

    with open('table.json', 'w') as file:
        file.write(json.dumps(table))


if __name__ == '__main__':
    read_pdf()