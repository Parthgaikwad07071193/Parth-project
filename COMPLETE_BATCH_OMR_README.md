# Enhanced Complete Batch OMR Processing System

This system extends the existing OMR scanner to provide comprehensive batch processing capabilities for PDF files containing multiple answer sheets, with enhanced features including camera capture, QR code recognition, digital signature verification, and advanced OCR.

## Features

1. **PDF Batch Processing**: Process multi-page PDFs with multiple answer sheets
2. **Automatic Answer Key Extraction**: Extract answer keys from reference sheets
3. **Manual Answer Key Entry**: Option to manually enter answer keys
4. **Comprehensive Reporting**: Generate detailed PDF and CSV reports
5. **Enhanced Student Information Extraction**: Advanced OCR for all metadata fields
6. **Visual Results Display**: Interactive dashboard for viewing results
7. **Camera Capture**: Direct photo upload from webcam/mobile camera
8. **QR Code Recognition**: For unique sheet/candidate identification
9. **Digital Signature Verification**: Recognize and validate signatures
10. **Skew Correction**: Automatic correction of skewed scans
11. **Multiple Markings Handling**: Detection and handling of multiple markings
12. **Analytics Dashboard**: Detailed statistics and performance insights
13. **Interactive Review**: Manual adjustment of detected answers

## System Requirements

- Python 3.7 or higher
- Required Python packages (automatically installed by startup script):
  - streamlit
  - opencv-python
  - numpy
  - Pillow
  - pandas
  - PyMuPDF
  - reportlab
  - pytesseract
  - pydantic
  - fastapi
  - uvicorn
  - python-multipart
  - pyzbar
  - scikit-image
  - streamlit-webrtc

## How to Use

### 1. Start the Application

Double-click on `start_complete_batch_omr.bat` or run it from the command line:

```cmd
start_complete_batch_omr.bat
```

The application will start on http://localhost:8503

### 2. Setup Answer Key

You have four options:

**Option A: Upload Reference Sheet**
- Upload a scanned image of an answer sheet with all correct answers marked
- Click "Extract Answer Key" to automatically detect the answers

**Option B: Select Existing Key**
- Choose from pre-existing answer keys in the `answer_keys` directory

**Option C: Manual Entry**
- Manually select the correct answer for each of the 30 questions

**Option D: Camera Capture**
- Use your webcam to capture a reference sheet in real-time

### 3. Process Sheets

Choose from three processing modes:

**Mode 1: Batch Processing**
- Upload PDF files with multiple answer sheets
- Upload multiple image files
- Capture multiple sheets using camera

**Mode 2: Single Sheet Processing**
- Process individual sheets with enhanced features
- QR code detection
- Digital signature verification
- Skew correction

**Mode 3: Analytics Dashboard**
- View detailed statistics
- Question-wise analysis
- Grade distribution
- Performance insights

### 4. Interactive Review

- Manually review and adjust detected answers
- Export individual reports
- View detailed question analysis

### 5. Download Reports

- Download comprehensive PDF and CSV reports
- Reports include all processing results and analysis

## File Structure

```
backend/
├── complete_batch_omr_app.py    # Main Streamlit application
├── pdf_batch_processor.py       # PDF batch processing logic
├── enhanced_omr_utils.py        # Enhanced OMR processing
├── reference_answer_extractor.py # Reference sheet answer extraction
├── pdf_processor.py             # PDF processing utilities
├── pdf_generator.py             # Report generation
├── models.py                    # Data models
├── answer_keys/                 # Directory for answer key files
├── batch_uploads/               # Temporary upload directory
├── batch_results/               # Results output directory
├── data/                        # Persistent data storage
└── temp/                        # Temporary processing directory
```

## Technical Details

### Enhanced Image Processing Pipeline

1. **Preprocessing**: 
   - Grayscale conversion
   - Contrast enhancement using CLAHE
   - Gaussian blur for noise reduction
   - Adaptive thresholding for binary conversion
   - Skew correction using perspective transformation

2. **Bubble Detection**:
   - Contour detection using OpenCV
   - Circular shape filtering
   - Position-based grouping for questions
   - Multiple marking detection

3. **Fill Analysis**:
   - Pixel density calculation for each bubble
   - Threshold-based marking detection
   - Handling of partial fills

### Advanced OCR Features

1. **Enhanced Student Information Extraction**:
   - Name extraction with pattern matching
   - Roll number detection
   - Batch and paper number recognition
   - Date extraction
   - Test type identification (Pre-test/Post-test)

2. **Handwriting Recognition**:
   - Contrast enhancement for better OCR
   - Multiple OCR passes with different configurations
   - Pattern-based text extraction

### Camera Capture

- Real-time webcam integration using WebRTC
- Direct photo capture and processing
- Mobile-friendly interface
- Instant processing of captured images

### QR Code Recognition

- Automatic detection and decoding of QR codes
- Unique sheet/candidate identification
- Error correction for damaged QR codes

### Digital Signature Verification

- Detection of signature areas in sheets
- Basic verification using edge detection
- Integration with advanced verification systems

### PDF Processing

- Uses PyMuPDF (fitz) for efficient PDF page extraction
- Converts each PDF page to high-quality JPEG image
- Processes each page as an individual answer sheet

### Reporting

- **PDF Reports**: Detailed analysis with charts and individual student reports
- **CSV Reports**: Structured data for further analysis in spreadsheets
- **Individual Reports**: Per-sheet detailed analysis

## Menu Options

### Answer Key Setup
- Setup answer keys using various methods
- Save and load answer keys
- Manual entry with validation

### Batch Processing
- Process multiple sheets in bulk
- Support for PDF and image files
- Camera capture for instant scanning

### Single Sheet Processing
- Enhanced processing of individual sheets
- QR code and signature detection
- Skew correction

### Analytics Dashboard
- Detailed statistics and insights
- Question-wise performance analysis
- Grade distribution visualization

### Interactive Review
- Manual review and adjustment
- Individual report generation
- Detailed question analysis

## Troubleshooting

### Common Issues

1. **PDF Processing Errors**:
   - Ensure PyMuPDF is installed: `pip install PyMuPDF`
   - Check PDF file integrity

2. **Answer Key Extraction Failures**:
   - Ensure reference sheet image quality is good
   - Check that all correct answers are clearly marked

3. **Camera Capture Issues**:
   - Ensure camera permissions are granted
   - Check that no other application is using the camera

4. **OCR Failures**:
   - Ensure Tesseract OCR is installed and in PATH
   - Check image quality and contrast

5. **Performance Issues**:
   - Processing time increases with PDF size
   - Close other applications to free up system resources

### Improving Accuracy

1. **Image Quality**:
   - Use high-resolution scans (300 DPI or higher)
   - Ensure good contrast between filled and empty bubbles
   - Avoid glare or shadows on the sheets

2. **Bubble Marking**:
   - Fill bubbles completely and darkly
   - Avoid stray marks on the sheet
   - Use consistent marking technique

3. **Text Fields**:
   - Write clearly and legibly
   - Use dark ink for better OCR
   - Avoid cursive handwriting

## Customization

### Adding New Answer Keys

1. Create a JSON file with the following format:
```json
{
  "1": "A",
  "2": "B",
  "3": "C",
  "...": "..."
}
```

2. Save the file in the `backend/answer_keys/` directory

### Modifying Processing Parameters

Edit `backend/enhanced_omr_utils.py` to adjust:
- Bubble detection thresholds
- Image preprocessing parameters
- Scoring algorithms

### Extending Features

The system is designed to be modular and extensible:
- Add new OCR extraction patterns
- Implement advanced signature verification
- Integrate machine learning models for better accuracy
- Add support for different sheet layouts

## Support

For issues or questions, please check:
1. The console output for error messages
2. The log files in the `backend/temp/` directory
3. Ensure all required dependencies are installed

The system is designed to be robust and handle various input formats, but image quality significantly affects accuracy.