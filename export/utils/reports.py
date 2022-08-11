import os
from typing import Union
from io import BytesIO
from admin.settings.base import MEDIA_ROOT, MEDIA_URL
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Line, Circle, String
from reportlab.platypus.doctemplate import Indenter
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from svglib.svglib import svg2rlg

"""
Reportlab documentation:
https://docs.reportlab.com/reportlab/userguide/ch1_intro/
source:
https://github.com/Distrotech/reportlab
"""

styles = getSampleStyleSheet()

class PDFBuilder:
      """
      Common parent class for PDF reports.
      Exposes write_nested_data and build methods, as well as utility methods
      for subclasses.
      """

      def __init__(self):
            self._story = []


      def __add_spacer(self, depth_level: int, indent=True) -> None:
            """
            Adds gap and indentation depending on depth level
            (for a lower depth the gap will be higher)
            """
            mul = len(self.write_handlers) - depth_level
            self._story.append(Spacer(0, mul * 1.75 * mm))
            if indent:
                  self._story.append(Indenter(
                        left = mul * mm, right = mul * mm
                  ))


      def __remove_indentation(self, depth_level: int) -> None:
            """
            Removes indentation depending on depth level
            (for a lower depth the indentation will be higher)
            """
            mul = len(self.write_handlers) - depth_level
            self._story.append(Indenter(
                  left = -mul * mm, right = -mul * mm
            ))


      def _get_sized_image(self, url: str, size=cm) -> Union[Image, Drawing]:
            """
            Creates and returns a sized image of a png, jpg or svg specified
            at url.
            """
            if url.endswith('svg'):
                  drawing = svg2rlg(url)
                  scale = size / drawing.height
                  drawing.width = size
                  drawing.height = size
                  drawing.scale(scale, scale)
                  return drawing
            return Image(url, width=size, height=size)


      def write_nested_data(self, category: str, data: dict, depth_level=0) -> None:
            """
            Iterates recursively through nested serialized data, and calls
            appropriate write_handler method for each nesting level
            """
            next_category = None
            next_data = None
            for key in data.keys():
                  if key in self.write_handlers.keys():
                        next_category = key
                        break

            if next_category:
                  next_data = data.pop(next_category)

            self.write_handlers[category](data)

            if not next_category:
                  return

            self.__add_spacer(depth_level - 1)

            depth_level += 1
            if isinstance(next_data, list):
                  for item in next_data:
                        self.write_nested_data(next_category, item, depth_level)
                        self.__add_spacer(depth_level, indent=False)
            else:
                  self.write_nested_data(next_category, next_data, depth_level)

            self.__remove_indentation(depth_level - 1)


      def build(self) -> BytesIO:
            """
            Builds and returns the PDF document
            """
            buffer = BytesIO()
            canvas = SimpleDocTemplate(
                  buffer,
                  leftMargin=cm,
                  rightMargin=cm,
                  topMargin=cm,
                  bottomMargin=cm
            )
            canvas.build(self._story)
            buffer.seek(0)
            return buffer


class AssessmentPDFReport(PDFBuilder):

      text_styles = {
            'doc_title': ParagraphStyle('DocTitle', fontSize=10),
            'heading1': ParagraphStyle(styles['Normal'], fontSize=14),
            'heading2': ParagraphStyle(styles['Normal'], fontSize=11),
            'question_order': ParagraphStyle(styles['Normal'], fontSize=7, textColor=HexColor('#7a7a7a'), alignment=TA_CENTER),
            'question_title': ParagraphStyle(styles['Normal'], fontSize=9, alignment=TA_CENTER),
            'answer': ParagraphStyle(styles['Normal'], fontSize=9, textColor=HexColor('#7a7a7a'), alignment=TA_CENTER),
            'answer_valid': ParagraphStyle(styles['Normal'], fontSize=9, textColor=HexColor('#63c7a9'), alignment=TA_CENTER)
      }

      def __init__(self):
            super().__init__()

            # Define methods that will be called by write_nested_data
            # (keys must correspond to keys in serialized data, associated to a dict or list)
            self.write_handlers = {
                  'assessments': self.__write_assessment,
                  'topics': self.__write_topic,
                  'questions': self.__write_question
            }


      def __get_paragraph_with_attachments(self, text: str,
            text_style: ParagraphStyle, attachments: list, img_size: int) -> list:
            """
            Creates a Paragraph containing specified attachments,
            or a [Drawing, Paragraph] if one of the attachments is an svg
            """
            icon = next(filter(lambda e: e['attachment_type'] == 'IMAGE', attachments), None)
            audio = next(filter(lambda e: e['attachment_type'] == 'AUDIO', attachments), None)
            atts_xml = ''
            svg_icon = None

            if icon:
                  try:
                        icon_url = os.path.join(MEDIA_ROOT, icon['file'].replace(MEDIA_URL, ''))
                        if icon_url.endswith('svg'):
                              svg_icon = self._get_sized_image(icon_url, img_size)
                              text_style = ParagraphStyle(
                                    text_style.fontName,
                                    fontSize=text_style.fontSize,
                                    textColor=text_style.textColor,
                                    alignment=TA_LEFT
                              )
                        else:
                              atts_xml = '<img src="{}" valign="middle" width="{}" height="{}"/>'.format(
                                    icon_url, img_size, img_size
                              )
                  except:
                        pass

            if audio:
                  audio_icon_url = os.path.join(MEDIA_ROOT, 'attachments/volume_up_FILL1_wght400_GRAD0_opsz48.png')
                  if icon:
                        atts_xml += '&nbsp;&nbsp;'
                  atts_xml += '<img src="{}" valign="middle" width="{}" height="{}"/>'.format(
                        audio_icon_url,
                        img_size,
                        img_size
                  )

            paragraph = Paragraph(
                  '<para>{}{}{}</para>'.format(
                        atts_xml,
                        '&nbsp;&nbsp;&nbsp;' if len(atts_xml) else '',
                        text
                  ), text_style
            )
            return [svg_icon, paragraph] if svg_icon else [paragraph]



      def __create_select_answer_table(self, answer: dict) -> Table:
            """
            Creates a Table object for a SELECT question answer
            """
            answer_title = answer['title'] if answer['title'] else ''
            answer_attachments = answer['attachments'] if answer['attachments'] else []

            text_style = self.text_styles['answer_valid'] if answer['valid'] else self.text_styles['answer']
            table_data = [[
                  Paragraph(answer_title, text_style)
            ]]
            table_style = [('VALIGN', (0, 0), (-1, 0), 'CENTER')]

            if 'attachments' in answer.keys() and len(answer['attachments']):
                  table_data = [self.__get_paragraph_with_attachments(
                        answer_title, text_style, answer_attachments, 14
                  )]
                  if len(table_data[0]) == 2:
                        table_style += [
                              ('ALIGN', (0, 0), (0, -1), 'RIGHT')
                        ]

            if answer['valid'] is True:
                  table_style += [
                        ('BOX', (0, 0), (-1, -1), .5, HexColor('#63c7a9')),
                        ('ROUNDEDCORNERS', [2] * 4),
                        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#63c7a9'))
                  ]

            table = Table(table_data)
            table.setStyle(TableStyle(table_style))
            return table


      def __create_numberline_slider(self, question: dict, slider_width: int) -> Drawing:
            """
            Creates a Drawing object containing the numberline slider and
            its text value
            """
            cursor_pos = question['expected_value'] / question['end'] * slider_width
            drawing_height = .15 * slider_width
            value_height = drawing_height / 4
            slider_height = .8 * drawing_height

            d = Drawing(slider_width, drawing_height)

            # slider fill area
            d.add(Line(0, slider_height, cursor_pos, slider_height,
                  strokeColor=HexColor('#3d8dd2'), strokeWidth=1
            ))

            # slider background
            d.add(Line(cursor_pos, slider_height, d.width, slider_height,
                  strokeColor=HexColor('#afafaf'), strokeWidth=1
            ))

            # cursor
            d.add(Circle(cursor_pos, slider_height, 2, fillColor=HexColor('#174c81')))

            # expected value
            d.add(String(cursor_pos - 2.5, value_height, str(question['expected_value']),
                  fontSize=10, fonFamily='sans-serif', fillColor=HexColor('#6a6a6a')
            ))
            return d


      def __write_question(self, data: dict) -> None:
            """
            Writes an Assessment Topic Question info onto the PDF document
            """
            question_title = self.__get_paragraph_with_attachments(
                  data['title'], self.text_styles['question_title'],
                  data['attachments'],
                  14
            )
            if len(question_title) == 2:
                  question_title = Table([question_title])
                  question_title.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        ('ALIGN', (0, 0), (0, 0), 'RIGHT')
                  ]))
            table_data = [
                  [Paragraph('Q' + str(data['order']), self.text_styles['question_order'])],
                  [question_title]
            ]

            answers_table_data = []
            answers_table_style = [
                  ('TOPPADDING', (0, -1), (-1, -1), 12),
                  ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ]
            if data['question_type'] == 'SELECT' and len(data['options']):
                  opt_row = []
                  for opt in data['options']:
                        opt_row.append(
                              self.__create_select_answer_table(opt)
                        )
                  answers_table_data.append(opt_row)

            if data['question_type'] == 'INPUT':
                  answers_table_data.append([
                        Paragraph(data['valid_answer'], self.text_styles['answer'])
                  ])

            if data['question_type'] == 'NUMBER_LINE':
                  answers_table_data.append(
                        [self.__create_numberline_slider(data, 10*cm)]
                  )
                  answers_table_style = []

            table_data += answers_table_data

            table = Table(table_data, rowHeights=[None, .5 * cm, None], colWidths=[None])
            table.setStyle(TableStyle([
                  ('SPAN', (0, 0), (-1, 0)),
                  ('SPAN', (0, 1), (-1, 1)),
                  ('TOPPADDING', (0, 0), (-1, 0), 10),
                  ('LEFTPADDING', (0, -1), (-1, -1), 8),
                  ('RIGHTPADDING', (0, -1), (-1, -1), 8),
                  ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                  ('VALIGN', (0, 1), (-1, 1), 'MIDDLE'),
                  ('BOX', (0, 0), (-1, -1), 1, HexColor('#F3F3F7')),
                  ('ROUNDEDCORNERS', [2] * 4)
            ] + answers_table_style))
            self._story.append(table)


      def __write_topic(self, data: dict) -> None:
            """
            Writes an Assessment Topic icon & title onto the PDF document
            """
            try:
                  table_icon = [self._get_sized_image(os.path.join(MEDIA_ROOT, data['icon'].replace(MEDIA_URL, '')), .75 * cm)]
            except:
                  table_icon = []
            table_data = [table_icon + [Paragraph(
                  '{} · {} questions'.format(data['name'],  str(data['questions_nb'])),
                  self.text_styles['heading2'])
            ]]
            table = Table(table_data, colWidths=[1.5 * cm, None])
            table.setStyle(TableStyle([
                  ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                  ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            self._story.append(table)


      def __write_assessment(self, data: dict) -> None:
            """
            Writes an Assessment icon & title onto the PDF document
            """
            try:
                  table_icon = [self._get_sized_image(os.path.join(MEDIA_ROOT, data['icon'].replace(MEDIA_URL, '')))]
            except:
                  table_icon = []
            table_data = [table_icon + [Paragraph(data['title'], self.text_styles['heading1'])]]
            table = Table(table_data, colWidths=[1.5 * cm, None])
            table.setStyle(TableStyle([
                  ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            self._story.append(table)