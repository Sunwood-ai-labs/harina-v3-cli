"""Harina v3 - Receipt OCR using Gemini API with OpenAI-compatible format via LiteLLM."""

import base64
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import litellm
from PIL import Image


class ReceiptOCR:
    """Receipt OCR processor using Gemini API via LiteLLM."""

    def __init__(self, api_key: str, model_name: str = "gemini/gemini-1.5-flash"):
        """Initialize with API key and model."""
        self.api_key = api_key
        self.model_name = model_name
        # Set the API key for LiteLLM
        litellm.api_key = api_key

    def _load_xml_template(self) -> str:
        """Load XML template from file."""
        template_path = Path(__file__).parent / "receipt_template.xml"
        try:
            return template_path.read_text(encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Failed to load XML template: {e}") from e

    def _load_product_categories(self) -> str:
        """Load product categories from file."""
        categories_path = Path(__file__).parent / "product_categories.xml"
        try:
            return categories_path.read_text(encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Failed to load product categories: {e}") from e

    def process_receipt(self, image_path: Path) -> str:
        """Process receipt image and return XML format."""

        # Load and validate image
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}") from e

        # Convert image to base64
        image_base64 = self._image_to_base64(image)

        # Load XML template and product categories
        xml_template = self._load_xml_template()
        product_categories = self._load_product_categories()

        # Create prompt for receipt recognition
        prompt = f"""このレシート画像を分析して、以下のXML形式で情報を抽出してください：

{xml_template}

商品のカテゴリ分けには以下の分類を参考にしてください：

{product_categories}

各商品について、最も適切なカテゴリとサブカテゴリを選択してください。
情報が読み取れない場合は、該当する要素を空にするか省略してください。
数値は数字のみで出力し、通貨記号は含めないでください。
XMLタグのみを出力し、他の説明文は含めないでください。
"""

        try:
            # Create messages for LiteLLM
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]

            # Call LiteLLM
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("No response from Gemini API")

            response_text = response.choices[0].message.content

            # Extract XML from response
            xml_content = self._extract_xml(response_text)

            # Validate and format XML
            formatted_xml = self._format_xml(xml_content)

            return formatted_xml

        except Exception as e:
            raise RuntimeError(f"Failed to process receipt: {e}") from e

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Save to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        # Encode to base64
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')

    def _extract_xml(self, text: str) -> str:
        """Extract XML content from response text."""
        # Look for XML content between <receipt> tags
        xml_match = re.search(r'<receipt>.*?</receipt>', text, re.DOTALL)
        if xml_match:
            return xml_match.group(0)

        # If no complete receipt tag found, try to find any XML-like content
        xml_lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('<') or xml_lines:
                xml_lines.append(line)
                if line.endswith('</receipt>'):
                    break

        if xml_lines:
            return '\n'.join(xml_lines)

        # Fallback: wrap the entire response in receipt tags if it looks like XML content
        if '<' in text and '>' in text:
            return f"<receipt>\n{text.strip()}\n</receipt>"

        raise ValueError("No valid XML content found in response")

    def _format_xml(self, xml_content: str) -> str:
        """Format and validate XML content."""
        try:
            # Parse XML to validate structure
            root = ET.fromstring(xml_content)

            # Convert back to string with proper formatting
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)

            # Return formatted XML
            return reparsed.toprettyxml(indent="  ", encoding=None).strip()

        except ET.ParseError:
            # If parsing fails, try to clean up the XML
            cleaned_xml = self._clean_xml(xml_content)
            try:
                root = ET.fromstring(cleaned_xml)
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ", encoding=None).strip()
            except Exception:
                # If all else fails, return the original content
                return xml_content

    def _clean_xml(self, xml_content: str) -> str:
        """Clean up malformed XML content."""
        # Remove XML declaration if present
        xml_content = re.sub(r'<\?xml[^>]*\?>', '', xml_content)

        # Remove any text before the first < or after the last >
        xml_content = re.sub(r'^[^<]*', '', xml_content)
        xml_content = re.sub(r'>[^>]*$', '>', xml_content)

        # Ensure proper encoding of special characters
        xml_content = xml_content.replace('&', '&amp;')
        xml_content = xml_content.replace('<', '&lt;').replace('&lt;', '<', 1)  # Fix first <

        return xml_content.strip()