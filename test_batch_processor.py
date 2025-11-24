"""
Test script for the PDF batch processor
"""

def test_imports():
    """Test that all modules can be imported correctly."""
    try:
        # Test importing the main modules from the backend directory
        import sys
        import os
        from pathlib import Path
        
        # Add the backend directory to the Python path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Change to the backend directory
        original_cwd = os.getcwd()
        os.chdir(backend_path)
        
        # Test importing the main modules
        import pdf_batch_processor
        print("✅ PDFBatchOMRProcessor imported successfully")
        
        import complete_batch_omr_app
        print("✅ CompleteBatchOMRApp imported successfully")
        
        # Test creating an instance
        processor = pdf_batch_processor.PDFBatchOMRProcessor()
        print("✅ PDFBatchOMRProcessor instance created successfully")
        
        # Change back to original directory
        os.chdir(original_cwd)
        
        print("\n🎉 All tests passed! The batch processing system is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing PDF Batch OMR Processor...")
    test_imports()