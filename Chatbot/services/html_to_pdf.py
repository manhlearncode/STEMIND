import asyncio
import tempfile
import os
from typing import Optional
from playwright.async_api import async_playwright

class HTMLToPDFService:
    def __init__(self):
        self.playwright = None
        self.browser = None

    def convert_url_to_pdf(self, html_url: str, options: dict = None) -> Optional[bytes]:
        """
        Chuyển đổi HTML URL thành PDF bằng Playwright
        Returns: PDF content as bytes
        """
        try:
            return asyncio.run(self._convert_with_playwright(html_url, options))
        except Exception as e:
            print(f"❌ Lỗi chuyển đổi HTML thành PDF: {e}")
            return None

    async def _convert_with_playwright(self, html_url: str, options: dict = None) -> Optional[bytes]:
        """Sử dụng Playwright để chuyển đổi HTML thành PDF"""
        try:
            # Cấu hình mặc định
            default_options = {
                "format": "A4",
                "margin": {
                    "top": "20mm",
                    "right": "20mm",
                    "bottom": "20mm",
                    "left": "20mm"
                },
                "printBackground": True,
                "preferCSSPageSize": True
            }
            
            if options:
                default_options.update(options)
            
            # Khởi tạo Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            
            # Tạo page mới
            page = await self.browser.new_page()
            
            # Điều hướng đến URL
            await page.goto(html_url, wait_until='networkidle')
            
            # Đợi một chút để đảm bảo trang load hoàn toàn
            await page.wait_for_timeout(2000)
            
            # Tạo PDF
            pdf_bytes = await page.pdf(**default_options)
            
            # Đóng browser và playwright
            await self.browser.close()
            await self.playwright.stop()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"❌ Lỗi Playwright: {e}")
            # Đảm bảo cleanup
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            return None



    def convert_html_string_to_pdf(self, html_content: str, options: dict = None) -> Optional[bytes]:
        """
        Chuyển đổi HTML string thành PDF bằng Playwright
        Returns: PDF content as bytes
        """
        try:
            # Lưu HTML tạm thời và chuyển đổi
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(html_content)
                html_path = tmp_file.name
            
            # Chuyển đổi file HTML thành PDF
            html_url = f"file://{html_path}"
            pdf_content = asyncio.run(self._convert_with_playwright(html_url, options))
            
            # Xóa file tạm
            os.unlink(html_path)
            
            return pdf_content
            
        except Exception as e:
            print(f"❌ Lỗi chuyển đổi HTML string: {e}")
            return None

    def get_pdf_options(self, format_type: str = "A4") -> dict:
        """Lấy cấu hình PDF theo loại format"""
        options = {
            "A4": {
                "format": "A4",
                "margin": {
                    "top": "20mm",
                    "right": "20mm", 
                    "bottom": "20mm",
                    "left": "20mm"
                }
            },
            "Letter": {
                "format": "Letter",
                "margin": {
                    "top": "0.5in",
                    "right": "0.5in",
                    "bottom": "0.5in", 
                    "left": "0.5in"
                }
            },
            "Legal": {
                "format": "Legal",
                "margin": {
                    "top": "20mm",
                    "right": "20mm",
                    "bottom": "20mm",
                    "left": "20mm"
                }
            }
        }
        
        return options.get(format_type, options["A4"])
