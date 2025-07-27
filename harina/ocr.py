"""Harina v3 - Receipt OCR using Gemini API with OpenAI-compatible format via LiteLLM."""

import litellm
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import base64
import io


class ReceiptOCR:
    """Receipt OCR processor using Gemini API via LiteLLM."""
    
    def __init__(self, api_key: str, model_name: str = "gemini/gemini-1.5-flash"):
        """Initialize with API key and model."""
        self.api_key = api_key
        self.model_name = model_name
        # Set the API key for LiteLLM
        litellm.api_key = api_key
        
    def process_receipt(self, image_path: Path) -> str:
        """Process receipt image and return XML format."""
        
        # Load and validate image
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")
        
        # Convert image to base64
        image_base64 = self._image_to_base64(image)
        
        # Create prompt for receipt recognition
        prompt = """
        このレシート画像を分析して、以下のXML形式で情報を抽出してください：

        <receipt>
            <store_info>
                <name>店舗名</name>
                <address>住所</address>
                <phone>電話番号</phone>
            </store_info>
            <transaction_info>
                <date>日付 (YYYY-MM-DD)</date>
                <time>時刻 (HH:MM)</time>
                <receipt_number>レシート番号</receipt_number>
            </transaction_info>
            <items>
                <item>
                    <name>商品名</name>
                    <quantity>数量</quantity>
                    <unit_price>単価</unit_price>
                    <total_price>合計金額</total_price>
                </item>
                <!-- 他の商品も同様に -->
            </items>
            <totals>
                <subtotal>小計</subtotal>
                <tax>税額</tax>
                <total>合計金額</total>
            </totals>
            <payment_info>
                <method>支払い方法</method>
                <amount_paid>支払い金額</amount_paid>
                <change>お釣り</change>
            </payment_info>
        </receipt>

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
            raise RuntimeError(f"Failed to process receipt: {e}")
    
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
            
        except ET.ParseError as e:
            # If parsing fails, try to clean up the XML
            cleaned_xml = self._clean_xml(xml_content)
            try:
                root = ET.fromstring(cleaned_xml)
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ", encoding=None).strip()
            except:
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