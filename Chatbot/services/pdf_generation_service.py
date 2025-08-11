import os
import tempfile
from io import BytesIO
from datetime import datetime
import markdown
import re
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFGenerationService:
    def __init__(self):
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#006065'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Oblique'
        ))
        
        # Heading 1 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#006065'),
            fontName='Helvetica-Bold'
        ))
        
        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#007a82'),
            fontName='Helvetica-Bold'
        ))
        
        # Heading 3 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#006065'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=10,
            fontName='Courier',
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#e9ecef'),
            borderWidth=1,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12
        ))
        
        # Exercise style
        self.styles.add(ParagraphStyle(
            name='Exercise',
            parent=self.styles['Normal'],
            fontSize=12,
            backColor=colors.HexColor('#e8f4f4'),
            borderColor=colors.HexColor('#006065'),
            borderWidth=1,
            leftIndent=15,
            rightIndent=15,
            spaceBefore=10,
            spaceAfter=10,
            fontName='Helvetica'
        ))
        
        # Answer style
        self.styles.add(ParagraphStyle(
            name='Answer',
            parent=self.styles['Normal'],
            fontSize=12,
            backColor=colors.HexColor('#fff3cd'),
            borderColor=colors.HexColor('#ffc107'),
            borderWidth=1,
            leftIndent=15,
            rightIndent=15,
            spaceBefore=8,
            spaceAfter=8,
            fontName='Helvetica'
        ))

    def markdown_to_elements(self, markdown_text):
        """Convert markdown to ReportLab elements"""
        # Convert markdown to HTML first
        md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'toc',
            'tables',
            'fenced_code'
        ])
        html_content = md.convert(markdown_text)
        
        # Parse HTML and convert to ReportLab elements
        elements = []
        
        # Split content by lines for processing
        lines = markdown_text.split('\n')
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    # Add current paragraph
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                continue
            
            # Check for headers
            if line.startswith('# '):
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line[2:], 'CustomHeading1'))
                continue
            elif line.startswith('## '):
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line[3:], 'CustomHeading2'))
                continue
            elif line.startswith('### '):
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line[4:], 'CustomHeading3'))
                continue
            
            # Check for lists
            elif line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph('• ' + line[2:], 'CustomBody'))
                continue
            elif re.match(r'^\d+\. ', line):
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line, 'CustomBody'))
                continue
            
            # Check for special content
            elif 'Bài tập' in line and ':' in line:
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line, 'Exercise'))
                continue
            elif 'Đáp án' in line and ':' in line:
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    elements.append(self._create_paragraph(text, 'CustomBody'))
                    current_paragraph = []
                elements.append(self._create_paragraph(line, 'Answer'))
                continue
            
            # Regular paragraph content
            else:
                current_paragraph.append(line)
        
        # Add remaining paragraph
        if current_paragraph:
            text = ' '.join(current_paragraph)
            elements.append(self._create_paragraph(text, 'CustomBody'))
        
        return elements

    def _create_paragraph(self, text, style_name):
        """Create a paragraph with the specified style"""
        # Clean up text formatting
        text = self._format_text(text)
        return Paragraph(text, self.styles[style_name])

    def _format_text(self, text):
        """Format text with basic markdown-like formatting"""
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Italic text
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Code text
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        
        return text

    def _create_header(self, title, subject=None, grade=None, generated_date=None):
        """Create document header"""
        elements = []
        
        # Title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtitle
        if subject and grade:
            subtitle = f"{subject} - {grade}"
            elements.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        
        # Date
        if generated_date:
            date_text = f"Ngày tạo: {generated_date}"
            elements.append(Paragraph(date_text, self.styles['CustomSubtitle']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements

    def _create_footer_canvas(self, canvas, doc):
        """Create footer for each page"""
        canvas.saveState()
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#ddd'))
        canvas.line(50, 50, A4[0] - 50, 50)
        
        # Footer text
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#666'))
        canvas.drawString(50, 35, "Tài liệu được tạo bởi STEMIND AI Assistant")
        canvas.drawRightString(A4[0] - 50, 35, f"Trang {doc.page}")
        
        canvas.restoreState()

    def generate_pdf_from_markdown(self, markdown_content, title=None, subject=None, grade=None):
        """Generate PDF from markdown content"""
        try:
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content
            story = []
            
            # Add header
            generated_date = datetime.now().strftime('%d/%m/%Y %H:%M')
            header_elements = self._create_header(
                title or 'Tài liệu học tập',
                subject,
                grade,
                generated_date
            )
            story.extend(header_elements)
            
            # Add main content
            content_elements = self.markdown_to_elements(markdown_content)
            story.extend(content_elements)
            
            # Add footer space
            story.append(Spacer(1, 0.5*inch))
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_footer_canvas, onLaterPages=self._create_footer_canvas)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Lỗi khi tạo PDF: {e}")
            raise Exception(f"Không thể tạo PDF: {str(e)}")

    def create_pdf_response(self, pdf_content, filename=None):
        """Create HTTP response for PDF download"""
        if not filename:
            filename = f"stemind_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Ensure filename has .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_content)
        
        return response

    def generate_lecture_pdf(self, content, topic, grade, subject):
        """Generate PDF specifically for lectures"""
        title = f"Bài giảng: {topic}"
        return self.generate_pdf_from_markdown(
            content, 
            title=title, 
            subject=subject, 
            grade=grade
        )

    def generate_exercise_pdf(self, content, topic, grade, subject):
        """Generate PDF specifically for exercises"""
        title = f"Bài tập: {topic}"
        return self.generate_pdf_from_markdown(
            content, 
            title=title, 
            subject=subject, 
            grade=grade
        )

    def generate_test_pdf(self, content, topic, grade, subject):
        """Generate PDF specifically for tests"""
        title = f"Bài kiểm tra: {topic}"
        return self.generate_pdf_from_markdown(
            content, 
            title=title, 
            subject=subject, 
            grade=grade
        )

    def generate_lesson_pdf(self, content, topic, grade, subject):
        """Generate PDF specifically for lessons"""
        title = f"Bài học: {topic}"
        return self.generate_pdf_from_markdown(
            content, 
            title=title, 
            subject=subject, 
            grade=grade
        )