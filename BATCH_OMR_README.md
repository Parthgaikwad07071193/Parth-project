# Enhanced Batch OMR Checker

A comprehensive OMR (Optical Mark Recognition) system designed for batch processing of student answer sheets with automatic name/roll number detection and detailed PDF reporting.

## 🌟 Key Features

### 📊 Batch Processing
- Process hundreds of student answer sheets in one go
- Real-time progress tracking
- Automatic error handling and recovery

### 🔍 OCR Integration
- Automatic detection of student names and roll numbers from handwritten text
- Uses EasyOCR for robust text recognition
- Handles various handwriting styles

### 📝 Reference Sheet Processing
- Upload a filled answer sheet as reference to automatically generate answer keys
- No need to manually enter correct answers
- Supports both reference sheet and manual answer key modes

### 📄 Comprehensive Reporting
- **PDF Reports**: Detailed reports with individual student analysis
- **CSV Export**: Spreadsheet-compatible data for further analysis
- **Summary Statistics**: Class performance overview
- **Grade Calculation**: Automatic grade assignment based on percentage

### 🎯 Advanced OMR Processing
- OpenCV-based bubble detection
- Adaptive thresholding for various image qualities
- Robust contour analysis for accurate marking detection

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r enhanced_requirements.txt
```

### Required Dependencies
- `streamlit` - Web interface
- `opencv-python` - Image processing
- `easyocr` - Text recognition
- `reportlab` - PDF generation
- `pandas` - Data manipulation
- `pillow` - Image handling

### Running the Application
```bash
streamlit run batch_omr_app.py
```

## 📋 Usage Guide

### Step 1: Setup Answer Key
Choose one of two methods:

#### Method A: Reference Sheet
1. Upload a completed answer sheet with correct answers marked
2. Click "Extract Answer Key from Reference"
3. Review the automatically detected answers

#### Method B: Existing Answer Key
1. Select from existing JSON answer keys
2. Or create a new answer key manually

### Step 2: Upload Student Sheets
1. Upload multiple student answer sheets (JPG, PNG)
2. Ensure names and roll numbers are clearly written
3. Preview uploaded files

### Step 3: Process Batch
1. Click "Start Batch Processing"
2. Monitor real-time progress
3. Review processing results

### Step 4: Download Reports
1. Generate comprehensive PDF report
2. Export CSV data for analysis
3. Clear results when done

## 📁 Project Structure

```
omr-scanner/
├── backend/
│   ├── batch_omr_app.py           # Main Streamlit application
│   ├── enhanced_omr_utils.py      # Enhanced OMR processor with OCR
│   ├── pdf_generator.py           # PDF report generation
│   ├── enhanced_requirements.txt  # Python dependencies
│   ├── batch_uploads/             # Temporary upload storage
│   ├── batch_results/             # Generated reports
│   ├── temp/                      # Temporary processing files
│   └── answer_keys/               # JSON answer key files
```

## 🔧 Configuration

### OMR Processing Parameters
Edit `enhanced_omr_utils.py` to adjust:
- `questions_per_row`: Number of answer choices (default: 5)
- `total_questions`: Total questions (default: 10)
- `bubble_threshold`: Fill detection threshold (default: 0.65)

### OCR Settings
- Language support: English (can be extended)
- Confidence threshold: 0.5 (adjustable)
- Text extraction region: Top 25% of image

### Grading Scale
Default grading scale (customizable in `pdf_generator.py`):
- A+: 90-100%
- A: 80-89%
- B+: 70-79%
- B: 60-69%
- C: 50-59%
- D: 40-49%
- F: Below 40%

## 📊 Report Features

### PDF Report Includes:
- **Title Page**: Exam details and summary
- **Statistics Section**: Class performance metrics
- **Detailed Results Table**: All students with scores and grades
- **Individual Reports**: Question-wise analysis for each student

### CSV Export Includes:
- Student information (name, roll number)
- Overall scores and percentages
- Individual question results
- Grade assignments

## 🎯 OMR Sheet Requirements

### For Best Results:
1. **Clear Images**: High contrast, well-lit photographs
2. **Proper Alignment**: Sheets should be reasonably straight
3. **Bubble Marking**: Use dark pen/pencil, fill bubbles completely
4. **Text Areas**: Write names and roll numbers clearly in designated areas
5. **Image Quality**: Minimum 300 DPI recommended

### Supported Formats:
- JPG/JPEG
- PNG
- Maximum file size: 5MB per image

## 🔍 Troubleshooting

### Common Issues:

#### OCR Not Detecting Names/Roll Numbers
- Ensure text is written clearly in the top portion of the sheet
- Use dark ink/pencil
- Avoid cursive handwriting when possible
- Check image quality and lighting

#### Bubble Detection Issues
- Verify bubbles are completely filled
- Ensure good contrast between marked and unmarked bubbles
- Check image alignment and quality
- Adjust threshold parameters if needed

#### Processing Errors
- Check image file formats and sizes
- Ensure sufficient system memory for batch processing
- Verify all dependencies are installed correctly

### Performance Tips:
- Process images in smaller batches (50-100 at a time) for better performance
- Use high-quality, well-lit images
- Ensure consistent OMR sheet layout across all students

## 🚀 Advanced Features

### Batch Processing Capabilities:
- **Parallel Processing**: Efficient handling of multiple images
- **Error Recovery**: Continue processing even if some images fail
- **Progress Tracking**: Real-time status updates
- **Memory Management**: Automatic cleanup of temporary files

### Reporting Features:
- **Customizable Templates**: Modify PDF layout and styling
- **Multiple Export Formats**: PDF, CSV, and JSON support
- **Statistical Analysis**: Comprehensive performance metrics
- **Individual Analysis**: Detailed question-wise breakdown

## 🔒 Security & Privacy

- **Local Processing**: All data processed locally, no cloud uploads
- **Temporary Files**: Automatic cleanup of uploaded images
- **Data Protection**: No permanent storage of student images
- **Secure Reports**: Generated reports stored locally

## 🤝 Support & Contribution

### Getting Help:
1. Check the troubleshooting section
2. Review configuration parameters
3. Ensure all dependencies are properly installed
4. Test with sample images first

### Contributing:
- Report bugs and issues
- Suggest new features
- Contribute code improvements
- Share sample OMR templates

## 📈 Performance Metrics

### Typical Processing Speed:
- **Single Sheet**: 2-5 seconds
- **Batch of 100**: 5-10 minutes
- **OCR Processing**: 1-2 seconds per sheet
- **Report Generation**: 10-30 seconds

### System Requirements:
- **RAM**: Minimum 4GB, recommended 8GB+
- **CPU**: Multi-core processor recommended
- **Storage**: 1GB free space for temporary processing
- **Python**: 3.8 or higher

## 🔄 Version History

### v2.0 (Current)
- ✅ Batch processing capabilities
- ✅ OCR integration for name/roll detection
- ✅ Reference sheet processing
- ✅ PDF report generation
- ✅ Enhanced Streamlit interface

### v1.0 (Previous)
- ✅ Single sheet processing
- ✅ Basic OMR detection
- ✅ FastAPI backend
- ✅ React frontend

---

## 📞 Contact & Support

For technical support or feature requests, please refer to the project documentation or create an issue in the project repository.

**Happy OMR Processing! 🎯**
