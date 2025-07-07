#!/usr/bin/env python3
"""
Create a test PDF for the RAG system
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def create_test_pdf():
    """Create a test PDF with Qualcomm Linux content"""
    
    # Create the PDF
    c = canvas.Canvas("pdfs/qualcomm_linux_test.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, 10*inch, "Qualcomm Linux System Manual")
    
    # Content
    c.setFont("Helvetica", 12)
    y_position = 9*inch
    
    content = [
        "Qualcomm Linux is a comprehensive operating system designed for Qualcomm processors.",
        "It provides optimized performance and power management for mobile and embedded devices.",
        "",
        "Key Features:",
        "• Advanced power management",
        "• Optimized kernel for ARM architecture", 
        "• Enhanced security features",
        "• Real-time processing capabilities",
        "",
        "System Requirements:",
        "• Qualcomm Snapdragon processor",
        "• Minimum 2GB RAM",
        "• 8GB storage space",
        "• ARM64 architecture support",
        "",
        "Installation Process:",
        "1. Download the Qualcomm Linux image",
        "2. Flash to device using fastboot",
        "3. Configure system settings",
        "4. Install additional packages as needed",
        "",
        "Development Tools:",
        "• Qualcomm SDK for Linux",
        "• Cross-compilation toolchain",
        "• Debug utilities and profilers",
        "• Performance monitoring tools",
        "",
        "Troubleshooting:",
        "Common issues include boot failures, driver compatibility, and performance optimization.",
        "Refer to the troubleshooting guide for detailed solutions and workarounds."
    ]
    
    for line in content:
        if line.startswith("•"):
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y_position, line)
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4."):
            c.setFont("Helvetica", 10)
            c.drawString(1.2*inch, y_position, line)
        else:
            c.setFont("Helvetica", 12)
            c.drawString(1*inch, y_position, line)
        
        y_position -= 0.25*inch
        
        # Add new page if needed
        if y_position < 1*inch:
            c.showPage()
            y_position = 10*inch
            c.setFont("Helvetica", 12)
    
    c.save()
    print("Test PDF created: pdfs/qualcomm_linux_test.pdf")

if __name__ == "__main__":
    create_test_pdf() 