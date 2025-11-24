# 🚀 Quick Start Guide - Enhanced Batch OMR Checker

## 📋 Prerequisites
- Python 3.8 or higher
- Windows/Linux/Mac system
- At least 4GB RAM (8GB recommended for large batches)

## ⚡ Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
cd "f:\omr scanner\backend"
pip install -r enhanced_requirements.txt
```

**OR** simply double-click: `start_batch_omr.bat`

### Step 2: Start the Application
```bash
streamlit run batch_omr_app.py
```

### Step 3: Open in Browser
The app will automatically open at: `http://localhost:8501`

## 🎯 First Time Usage

### Option A: Using Reference Answer Sheet
1. **Upload Reference Sheet**: Upload a completed answer sheet with correct answers marked
2. **Extract Answers**: Click "Extract Answer Key from Reference" 
3. **Upload Student Sheets**: Upload multiple student answer sheets
4. **Process**: Click "Start Batch Processing"
5. **Download**: Generate and download PDF/CSV reports

### Option B: Using Manual Answer Key
1. **Create Answer Key**: Enter correct answers manually or select existing JSON file
2. **Upload Student Sheets**: Upload multiple student answer sheets  
3. **Process**: Click "Start Batch Processing"
4. **Download**: Generate and download PDF/CSV reports

## 📊 Sample Workflow

```
Reference Sheet (Teacher's completed sheet)
    ↓
Extract Answer Key (A, B, C, D, A, B, C, D, A, B)
    ↓
Upload Student Sheets (100 student images)
    ↓
Batch Processing (OCR + OMR analysis)
    ↓
Results (Names, Roll Numbers, Scores, Grades)
    ↓
PDF Report + CSV Export
```

## 🔧 Troubleshooting

### Common Issues:

**1. Import Errors**
```bash
pip install --upgrade pip
pip install -r enhanced_requirements.txt
```

**2. OCR Not Working**
- Ensure student names/roll numbers are written clearly
- Use dark pen/pencil for writing
- Check image quality and lighting

**3. Bubble Detection Issues**
- Fill bubbles completely with dark pen/pencil
- Ensure good image contrast
- Check image alignment

**4. Memory Issues (Large Batches)**
- Process in smaller batches (50-100 images)
- Close other applications
- Ensure sufficient RAM

## 📁 File Structure After Setup
```
omr scanner/
├── backend/
│   ├── batch_omr_app.py          # Main Streamlit app
│   ├── enhanced_omr_utils.py     # OMR processor with OCR
│   ├── pdf_generator.py          # PDF report generator
│   ├── enhanced_requirements.txt # Dependencies
│   ├── answer_keys/              # JSON answer keys
│   ├── batch_uploads/            # Temporary uploads
│   ├── batch_results/            # Generated reports
│   └── temp/                     # Processing temp files
├── start_batch_omr.bat          # Windows startup script
└── QUICK_START.md               # This guide
```

## 🎯 Tips for Best Results

### Image Quality:
- **Resolution**: Minimum 300 DPI
- **Lighting**: Even, bright lighting
- **Contrast**: High contrast between marks and paper
- **Alignment**: Keep sheets reasonably straight

### Student Information:
- **Names**: Write clearly in BLOCK LETTERS
- **Roll Numbers**: Use clear, distinct digits
- **Location**: Write in the top portion of the sheet

### Bubble Marking:
- **Fill Completely**: Dark, solid fills
- **Single Answer**: One bubble per question
- **Dark Pen/Pencil**: Use #2 pencil or dark pen

## 📞 Need Help?

1. **Check the detailed README**: `BATCH_OMR_README.md`
2. **Run the test script**: `python test_setup.py`
3. **Verify installation**: Check all dependencies are installed
4. **Test with sample images**: Start with 2-3 test images first

## 🎉 You're Ready!

Your enhanced OMR checker is now ready to process hundreds of student answer sheets with automatic name detection and professional reporting!

**Happy OMR Processing! 📊**
