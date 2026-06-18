from io import BytesIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

class ExportService:
    @staticmethod
    def export_to_excel(data: list, columns: list, filename: str = "report.xlsx"):
        """Export data to Excel"""
        if not data:
            return None
        
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            # Auto-adjust column widths
            for column in df:
                column_length = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                writer.sheets['Data'].column_dimensions[chr(65 + col_idx)].width = min(column_length + 2, 30)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_pdf(data: list, columns: list, title: str = "Report"):
        """Export data to PDF"""
        if not data:
            return None
        
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#f97316'),
            alignment=1,  # Center
            spaceAfter=30
        )
        
        elements = []
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Table data
        table_data = [columns]
        for row in data[:1000]:  # Limit to 1000 rows for PDF
            table_data.append([row.get(col, '') for col in columns])
        
        # Table style
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        return output