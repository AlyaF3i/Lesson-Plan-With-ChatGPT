from fpdf import FPDF


def create_lesson_plan_pdf(lesson_dict):
    # Create a PDF class by inheriting from FPDF
    class PDF(FPDF):
        def header(self):
            # Set the font and size for the header text
            self.set_font('Courier', 'B', 29)

            # Add the header text
            self.cell(0, 10, 'LESSON PLAN', 0, 1, 'C', fill=False)
            self.ln(10)

            # Add the image to the header
            self.image('school.jpeg', x=10, y=10, w=35, h=10)

        def chapter_title(self, title):
            # Set the font and size for the chapter title
            self.set_font('Courier', 'B', 15)
            self.set_text_color(0, 0, 0)  # Black color
            self.cell(0, 10, title, 0, 1, 'L', fill=False)
            self.ln(5)

        def chapter_body(self, text):
            # Set the font and size for the chapter body
            self.set_font('Arial', '', 12)
            self.set_text_color(0, 0, 0)  # Black color
            self.multi_cell(0, 5, text)
            self.ln()

        def bullet_list(self, items, style='bullet'):
            # Set the font and size for the bullet list
            self.set_font('Arial', '', 12)
            self.set_text_color(0, 0, 0)  # Black color

            if style == 'bullet':
                bullet = chr(149)  # Bullet character (•)
            elif style == 'numbered':
                bullet = ''
            else:
                return

            # Add each item as a bullet point
            for index, item in enumerate(items, start=1):
                if style == 'numbered':
                    bullet = f'{index}.'
                self.cell(5, 5, bullet, 0, 0, 'L')  # Add bullet point
                self.multi_cell(0, 5, item)
                self.ln()

    # Initialize the PDF object
    pdf = PDF()
    pdf.add_page()

    # Add the lesson details
    pdf.chapter_title('Lesson Details')

    # Create a table-like structure using the Cell() method
    pdf.set_fill_color(210, 220, 245)  # Set the background color for the table
    # Set the font and size for the table headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Field', 1, 0, 'C', fill=True)
    pdf.cell(120, 10, 'Value', 1, 1, 'C', fill=True)

    # Set the font and size for the table content
    pdf.set_font('Arial', '', 12)
    # Set the background color for the table content
    pdf.set_fill_color(255, 255, 255)
    for key, value in lesson_dict.items():
        if key == 'Supporting material':
            value = value[:60] if len(value) > 60 else value
        if isinstance(value, dict) or isinstance(value, list):
            continue  # Skip nested dictionaries and lists
        pdf.cell(40, 10, key, 1, 0, 'L', fill=True)
        pdf.cell(120, 10, str(value), 1, 1, 'L', fill=True)

    pdf.ln(10)  # Add some vertical spacing

    # Add the nested dictionaries and lists separately
    for key, value in lesson_dict.items():
        if isinstance(value, dict):
            pdf.chapter_title(key)
            for k, v in value.items():
                if isinstance(v, list):
                    pdf.chapter_body(f'{k}')
                    for vv in v:
                        pdf.chapter_body(f'-\t{vv}')
                else:
                    pdf.chapter_body(f'{k}: {v}')

            pdf.ln()
        elif isinstance(value, list):
            if key == 'Learning outcome':
                pdf.chapter_title(key)
                # Format as bullet points
                pdf.bullet_list(value, style='bullet')
                pdf.ln()
            elif key == 'Differentiation':
                pdf.chapter_title(key)
                # Format as bullet points
                pdf.bullet_list(value, style='bullet')
                pdf.ln()
            elif key == 'Learning experiences':
                pdf.chapter_title(key)
                for exp_key, exp_value in value.items():
                    pdf.chapter_body(f'{exp_key}:')
                    for item in exp_value:
                        print(item)
                        pdf.chapter_body(f'- {item}')
                        pdf.ln()  # Add a hyphen before each item
                    pdf.ln()
            elif key == 'Educator reflection':
                pdf.chapter_title(key)
                # Format as bullet points
                pdf.bullet_list(value, style='bullet')
                pdf.ln()
            else:
                pdf.chapter_title(key)
                for item in value:
                    pdf.chapter_body(f' - {item}')
                pdf.ln()

    # Save the PDF file with UTF-8 encoding
    pdf.set_compression(False)
    pdf.output('lesson_plan.pdf', 'F')
