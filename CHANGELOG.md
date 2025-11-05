# Changelog

All notable changes to LLMPrompt will be documented in this file.

## [2.0.0] - 2025-11-05

### Added
- **Preview Pane**: Real-time preview of the built prompt in a resizable right pane
- **Save/Load Configurations**: Save and load complete prompt setups as JSON files
- **Keyboard Shortcuts**:
  - Ctrl+B: Build and copy prompt
  - Ctrl+S: Save configuration
  - Ctrl+O: Load configuration
  - Ctrl+E: Export to file
  - Ctrl+R: Refresh preview
- **Search & Filter**: Real-time file filtering with search box
- **Recent Directories**: Dropdown showing 10 most recently used directories
- **File Count Indicators**: Display selected/total counts for each listbox (e.g., "5/20")
- **Select All/Deselect All**: Buttons for bulk selection in each listbox
- **Clear Buttons**: Quick reset buttons for each section
- **Export to File**: Save built prompts as text files
- **Menu Bar**: Organized File and Help menus
- **About Dialog**: Information about the application and its features
- **Keyboard Shortcuts Help**: Quick reference dialog
- **Resizable Sections**: PanedWindow for adjustable preview pane size

### Changed
- Increased window size from 1200x900 to 1400x950 to accommodate preview pane
- Improved error handling throughout the application
- Enhanced file reading with better exception handling
- Better layout organization with improved visual hierarchy
- Token count display now shown in bold for better visibility

### Fixed
- Bug on line 19: Changed `root.geometry()` to `self.master.geometry()` for consistency
- File reading now uses `errors='ignore'` for more robust UTF-8 handling
- Improved exception handling in directory and file operations

### Technical Improvements
- Added comprehensive docstrings to all methods
- Better code organization and readability
- Separated concerns with dedicated methods for each feature
- Added persistent storage for recent directories (JSON file)
- More robust configuration save/load with validation

## [1.0.0] - Previous Version

### Initial Features
- Multi-file selection from directory
- Meta prompts support
- Custom instructions support
- User text input
- Real-time token counting with tiktoken
- XML-structured output
- Clipboard integration
- UTF-8 file filtering
