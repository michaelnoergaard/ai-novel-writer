"""
Professional PDF formatter for AI-generated short stories
Theme-based styling with genre-appropriate formatting
"""

from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from ..models.basic_models import GeneratedStory, StoryGenre
try:
    from ..models.v13_models import AdvancedGeneratedStory
except ImportError:
    AdvancedGeneratedStory = None


class ThemeBasedPDFFormatter:
    """Creates professional PDF exports with theme-based styling"""
    
    def __init__(self):
        self.theme_configs = self._create_theme_configurations()
        
    def export_to_pdf(self, story, output_path: Path) -> Path:
        """Export story to a professionally formatted PDF"""
        
        # Handle both GeneratedStory and AdvancedGeneratedStory
        if hasattr(story, 'original_genre'):
            # V1.3+ AdvancedGeneratedStory
            display_genre = story.requirements.get_display_genre() if hasattr(story.requirements, 'get_display_genre') else story.genre
        else:
            # V1.1/V1.2 GeneratedStory
            display_genre = story.genre
        
        # Get theme configuration
        theme = self.theme_configs.get(story.genre, self.theme_configs[StoryGenre.LITERARY])
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        # Build story elements
        story_elements = []
        
        # Add title page
        story_elements.extend(self._create_title_page(story, theme, display_genre))
        
        # Add page break
        story_elements.append(PageBreak())
        
        # Add story content
        story_elements.extend(self._create_story_content(story, theme))
        
        # Add footer page with metadata
        story_elements.append(PageBreak())
        story_elements.extend(self._create_metadata_page(story, theme, display_genre))
        
        # Build PDF
        doc.build(story_elements)
        
        return output_path
    
    def _create_theme_configurations(self) -> Dict[StoryGenre, Dict]:
        """Create theme-specific styling configurations"""
        return {
            StoryGenre.LITERARY: {
                'primary_color': colors.Color(0.2, 0.2, 0.3),  # Deep blue-gray
                'accent_color': colors.Color(0.7, 0.6, 0.4),   # Warm gold
                'title_font': 'Times-Roman',
                'body_font': 'Times-Roman',
                'decorative_elements': True,
                'elegant_spacing': True
            },
            StoryGenre.MYSTERY: {
                'primary_color': colors.Color(0.1, 0.1, 0.1),  # Near black
                'accent_color': colors.Color(0.8, 0.1, 0.1),   # Deep red
                'title_font': 'Times-Bold',
                'body_font': 'Times-Roman',
                'decorative_elements': False,
                'elegant_spacing': False
            },
            StoryGenre.SCIENCE_FICTION: {
                'primary_color': colors.Color(0.0, 0.2, 0.4),  # Deep blue
                'accent_color': colors.Color(0.0, 0.8, 0.9),   # Cyan
                'title_font': 'Helvetica-Bold',
                'body_font': 'Helvetica',
                'decorative_elements': False,
                'elegant_spacing': False
            },
            StoryGenre.FANTASY: {
                'primary_color': colors.Color(0.3, 0.1, 0.4),  # Deep purple
                'accent_color': colors.Color(0.8, 0.7, 0.3),   # Golden
                'title_font': 'Times-Bold',
                'body_font': 'Times-Roman',
                'decorative_elements': True,
                'elegant_spacing': True
            },
            StoryGenre.ROMANCE: {
                'primary_color': colors.Color(0.4, 0.2, 0.3),  # Deep rose
                'accent_color': colors.Color(0.9, 0.7, 0.8),   # Light rose
                'title_font': 'Times-Italic',
                'body_font': 'Times-Roman',
                'decorative_elements': True,
                'elegant_spacing': True
            }
        }
    
    def _create_title_page(self, story, theme: Dict, display_genre: str) -> list:
        """Create an elegant title page"""
        elements = []
        
        # Large spacer to center title
        elements.append(Spacer(1, 2*inch))
        
        # Main title
        title_style = ParagraphStyle(
            'CustomTitle',
            fontName=theme['title_font'],
            fontSize=24,
            textColor=theme['primary_color'],
            alignment=TA_CENTER,
            spaceAfter=0.5*inch,
            fontVariant='small-caps' if theme.get('decorative_elements') else None
        )
        
        elements.append(Paragraph(story.title, title_style))
        
        # Decorative line if theme supports it
        if theme.get('decorative_elements'):
            line_style = ParagraphStyle(
                'DecorativeLine',
                fontName='Times-Roman',
                fontSize=16,
                textColor=theme['accent_color'],
                alignment=TA_CENTER,
                spaceAfter=0.5*inch
            )
            elements.append(Paragraph("◆ ◇ ◆", line_style))
        
        # Genre subtitle
        genre_style = ParagraphStyle(
            'Genre',
            fontName='Times-Italic',
            fontSize=12,
            textColor=theme['accent_color'],
            alignment=TA_CENTER,
            spaceAfter=1*inch
        )
        
        genre_text = f"A {display_genre.replace('_', ' ').replace('-', ' ').title()} Short Story"
        elements.append(Paragraph(genre_text, genre_style))
        
        # Spacer
        elements.append(Spacer(1, 1*inch))
        
        # Word count and generation date
        metadata_style = ParagraphStyle(
            'Metadata',
            fontName='Times-Roman',
            fontSize=10,
            textColor=theme['primary_color'],
            alignment=TA_CENTER,
            spaceAfter=0.2*inch
        )
        
        elements.append(Paragraph(f"Word Count: {story.word_count}", metadata_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", metadata_style))
        
        # Bottom attribution
        elements.append(Spacer(1, 1*inch))
        attr_style = ParagraphStyle(
            'Attribution',
            fontName='Times-Italic',
            fontSize=9,
            textColor=colors.Color(0.5, 0.5, 0.5),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Generated by AI Story Writer", attr_style))
        
        return elements
    
    def _create_story_content(self, story: GeneratedStory, theme: Dict) -> list:
        """Create formatted story content with proper typography"""
        elements = []
        
        # Story content style
        if theme.get('elegant_spacing'):
            # More elegant spacing for literary works
            body_style = ParagraphStyle(
                'StoryBody',
                fontName=theme['body_font'],
                fontSize=12,
                textColor=theme['primary_color'],
                alignment=TA_JUSTIFY,
                spaceAfter=14,
                leading=18,
                leftIndent=0,
                rightIndent=0
            )
            first_para_style = ParagraphStyle(
                'FirstParagraph',
                fontName=theme['body_font'],
                fontSize=12,
                textColor=theme['primary_color'],
                alignment=TA_JUSTIFY,
                spaceAfter=14,
                leading=18,
                leftIndent=0,
                rightIndent=0
            )
        else:
            # Standard formatting for genre fiction
            body_style = ParagraphStyle(
                'StoryBody',
                fontName=theme['body_font'],
                fontSize=11,
                textColor=theme['primary_color'],
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=15,
                leftIndent=24,  # Indent paragraphs
                rightIndent=0
            )
            first_para_style = ParagraphStyle(
                'FirstParagraph',
                fontName=theme['body_font'],
                fontSize=11,
                textColor=theme['primary_color'],
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=15,
                leftIndent=0,  # No indent for first paragraph
                rightIndent=0
            )
        
        # Split story into paragraphs
        paragraphs = [p.strip() for p in story.content.split('\n\n') if p.strip()]
        
        # Add first paragraph with special formatting
        if paragraphs:
            # Create drop cap effect for first letter if elegant
            if theme.get('decorative_elements') and len(paragraphs[0]) > 0:
                first_char = paragraphs[0][0].upper()
                rest_of_first = paragraphs[0][1:]
                
                drop_cap_style = ParagraphStyle(
                    'DropCap',
                    fontName=theme['title_font'],
                    fontSize=36,
                    textColor=theme['accent_color'],
                    alignment=TA_LEFT
                )
                
                # Create the drop cap paragraph
                first_para_text = f'<font name="{theme["title_font"]}" size="36" color="{theme["accent_color"].hexval()}">{first_char}</font>{rest_of_first}'
                elements.append(Paragraph(first_para_text, first_para_style))
            else:
                elements.append(Paragraph(paragraphs[0], first_para_style))
            
            # Add remaining paragraphs
            for paragraph in paragraphs[1:]:
                elements.append(Paragraph(paragraph, body_style))
        
        return elements
    
    def _create_metadata_page(self, story, theme: Dict, display_genre: str) -> list:
        """Create a metadata page with story information"""
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'MetadataTitle',
            fontName=theme['title_font'],
            fontSize=16,
            textColor=theme['primary_color'],
            alignment=TA_CENTER,
            spaceAfter=0.5*inch
        )
        
        elements.append(Paragraph("Story Information", title_style))
        
        # Metadata content
        meta_style = ParagraphStyle(
            'MetadataContent',
            fontName=theme['body_font'],
            fontSize=11,
            textColor=theme['primary_color'],
            alignment=TA_LEFT,
            spaceAfter=12,
            leading=15
        )
        
        # Story details
        metadata_items = [
            f"<b>Title:</b> {story.title}",
            f"<b>Genre:</b> {display_genre.replace('_', ' ').replace('-', ' ').title()}",
            f"<b>Length Category:</b> {story.requirements.length.title()} Fiction",
            f"<b>Word Count:</b> {story.word_count} words",
            f"<b>Target Word Count:</b> {story.requirements.target_word_count} words"
        ]
        
        if story.requirements.theme:
            metadata_items.append(f"<b>Theme:</b> {story.requirements.theme}")
        
        if story.requirements.setting:
            metadata_items.append(f"<b>Setting:</b> {story.requirements.setting}")
        
        metadata_items.extend([
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"<b>Generator:</b> AI Story Writer v1.0"
        ])
        
        for item in metadata_items:
            elements.append(Paragraph(item, meta_style))
        
        # Add some space
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer note
        footer_style = ParagraphStyle(
            'Footer',
            fontName='Times-Italic',
            fontSize=9,
            textColor=colors.Color(0.5, 0.5, 0.5),
            alignment=TA_CENTER
        )
        
        footer_text = """
        This story was generated using artificial intelligence and represents 
        an original work created specifically for this request. The content, 
        characters, and plot are products of AI creativity guided by the 
        specified parameters.
        """
        
        elements.append(Paragraph(footer_text, footer_style))
        
        return elements


def export_story_to_pdf(story: GeneratedStory, output_path: Path) -> Path:
    """Convenience function to export a story to PDF"""
    formatter = ThemeBasedPDFFormatter()
    return formatter.export_to_pdf(story, output_path)