"""Harina v3 - Receipt OCR using Gemini API with OpenAI-compatible format via LiteLLM."""

import base64
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import litellm
from loguru import logger
from PIL import Image


class ReceiptOCR:
    """Receipt OCR processor using Gemini API via LiteLLM."""

    def __init__(self, model_name: str = "gemini/gemini-1.5-flash"):
        """Initialize with model name."""
        self.model_name = model_name

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

    def process_receipt(self, image_path: Path, output_format: str = 'xml') -> str:
        """Process receipt image and return XML or CSV format."""

        # Load and validate image
        logger.debug(f"📂 Loading image: {image_path}")
        try:
            image = Image.open(image_path)
            logger.debug(f"✅ Image loaded successfully: {image.size} pixels, mode: {image.mode}")
        except Exception as e:
            logger.error(f"❌ Failed to load image: {e}")
            raise ValueError(f"Failed to load image: {e}") from e

        # Convert image to base64
        logger.debug("🔄 Converting image to base64...")
        image_base64 = self._image_to_base64(image)
        logger.debug(f"✅ Image converted to base64 ({len(image_base64)} characters)")

        # Load XML template and product categories
        logger.debug("📋 Loading XML template and product categories...")
        xml_template = self._load_xml_template()
        product_categories = self._load_product_categories()
        logger.debug("✅ Templates loaded successfully")

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
            logger.info("🤖 Preparing API request...")
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

            # Call LiteLLM (API key is read from environment variables automatically)
            logger.info(f"🌐 Calling {self.model_name} API...")
            response = litellm.completion(
                model=self.model_name,
                messages=messages
            )

            if not response.choices or not response.choices[0].message.content:
                logger.error("❌ No response from API")
                raise ValueError("No response from Gemini API")

            response_text = response.choices[0].message.content
            logger.info("✅ Received response from API")

            # Extract XML from response
            logger.info("🔍 Extracting XML content from response...")
            xml_content = self._extract_xml(response_text)
            logger.debug("✅ XML content extracted successfully")

            # Validate and format XML
            logger.info("📝 Formatting and validating XML...")
            formatted_xml = self._format_xml(xml_content)
            logger.info("✅ XML formatted and validated successfully")

            if output_format.lower() == 'csv':
                return self.convert_xml_to_csv(formatted_xml)
            else:
                return formatted_xml

        except Exception as e:
            logger.error(f"❌ Failed to process receipt: {e}")
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

            # Get formatted XML and clean up unwanted whitespace
            formatted_xml = reparsed.toprettyxml(indent="  ", encoding=None)
            
            # Remove excessive blank lines and clean up formatting
            cleaned_xml = self._remove_excessive_whitespace(formatted_xml)
            
            return cleaned_xml.strip()

        except ET.ParseError:
            # If parsing fails, try to clean up the XML
            cleaned_xml = self._clean_xml(xml_content)
            try:
                root = ET.fromstring(cleaned_xml)
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = minidom.parseString(rough_string)
                formatted_xml = reparsed.toprettyxml(indent="  ", encoding=None)
                cleaned_xml = self._remove_excessive_whitespace(formatted_xml)
                return cleaned_xml.strip()
            except Exception:
                # If all else fails, return the original content
                return xml_content

    def _remove_excessive_whitespace(self, xml_content: str) -> str:
        """Remove excessive whitespace and blank lines from XML content."""
        lines = xml_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip completely empty lines
            if line.strip() == '':
                continue
            # Skip lines with only whitespace that don't contain XML tags
            if not line.strip() or (line.strip() and '<' not in line and '>' not in line):
                continue
            cleaned_lines.append(line)
        
        # Join lines and remove multiple consecutive newlines
        result = '\n'.join(cleaned_lines)
        
        # Remove any remaining multiple newlines
        result = re.sub(r'\n\s*\n', '\n', result)
        
        return result

    def _clean_xml(self, xml_content: str) -> str:
        """Clean up malformed XML content."""
        # Remove XML declaration if present
        xml_content = re.sub(r'<\?xml[^>]*\?>', '', xml_content)

        # Remove any text before the first < or after the last >
        xml_content = re.sub(r'^[^<]*', '', xml_content)
        xml_content = re.sub(r'>[^>]*$', '>', xml_content)

        # Ensure proper encoding of special characters
        xml_content = xml_content.replace('&', '&')
        xml_content = xml_content.replace('<', '<').replace('<', '<', 1)  # Fix first <

        return xml_content.strip()

    def convert_xml_to_csv(self, xml_content: str) -> str:
        """Convert XML content to CSV format."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Prepare CSV header
            csv_lines = []
            header = ["store_name", "store_address", "store_phone",
                       "transaction_date", "transaction_time", "receipt_number",
                       "item_name", "item_category", "item_subcategory",
                       "item_quantity", "item_unit_price", "item_total_price",
                       "subtotal", "tax", "total",
                       "payment_method", "amount_paid", "change"]
            csv_lines.append(",".join(header))
            
            # Extract store info
            store_info = root.find("store_info")
            store_name = store_info.find("n").text or "" if store_info.find("n") is not None else ""
            store_address = store_info.find("address").text or "" if store_info.find("address") is not None else ""
            store_phone = store_info.find("phone").text or "" if store_info.find("phone") is not None else ""
            
            # Extract transaction info
            transaction_info = root.find("transaction_info")
            transaction_date = transaction_info.find("date").text or "" if transaction_info.find("date") is not None else ""
            transaction_time = transaction_info.find("time").text or "" if transaction_info.find("time") is not None else ""
            receipt_number = transaction_info.find("receipt_number").text or "" if transaction_info.find("receipt_number") is not None else ""
            
            # Extract totals
            totals = root.find("totals")
            subtotal = totals.find("subtotal").text or "" if totals.find("subtotal") is not None else ""
            tax = totals.find("tax").text or "" if totals.find("tax") is not None else ""
            total = totals.find("total").text or "" if totals.find("total") is not None else ""
            
            # Extract payment info
            payment_info = root.find("payment_info")
            payment_method = payment_info.find("method").text or "" if payment_info.find("method") is not None else ""
            amount_paid = payment_info.find("amount_paid").text or "" if payment_info.find("amount_paid") is not None else ""
            change = payment_info.find("change").text or "" if payment_info.find("change") is not None else ""
            
            # Extract items and create CSV rows
            items = root.find("items")
            if items is not None:
                for item in items.findall("item"):
                    item_name = item.find("n").text or "" if item.find("n") is not None else ""
                    item_category = item.find("category").text or "" if item.find("category") is not None else ""
                    item_subcategory = item.find("subcategory").text or "" if item.find("subcategory") is not None else ""
                    item_quantity = item.find("quantity").text or "" if item.find("quantity") is not None else ""
                    item_unit_price = item.find("unit_price").text or "" if item.find("unit_price") is not None else ""
                    item_total_price = item.find("total_price").text or "" if item.find("total_price") is not None else ""
                    
                    # Create CSV row
                    row = [store_name, store_address, store_phone,
                           transaction_date, transaction_time, receipt_number,
                           item_name, item_category, item_subcategory,
                           item_quantity, item_unit_price, item_total_price,
                           subtotal, tax, total,
                           payment_method, amount_paid, change]
                    csv_lines.append(",".join(row))
            else:
                # If no items, create a row with store and transaction info only
                row = [store_name, store_address, store_phone,
                       transaction_date, transaction_time, receipt_number,
                       "", "", "", "", "", "",
                       subtotal, tax, total,
                       payment_method, amount_paid, change]
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
            
        except ET.ParseError as e:
            logger.error(f"❌ Failed to parse XML for CSV conversion: {e}")
            raise ValueError(f"Failed to parse XML for CSV conversion: {e}") from e
        except Exception as e:
            logger.error(f"❌ Failed to convert XML to CSV: {e}")
            raise RuntimeError(f"Failed to convert XML to CSV: {e}") from e