# AI Project GD

## How to Run the Game

### Prerequisites
- Python 3.8 or higher
- Git

### Installation Steps

1. **Get the project files:**
   - **Option A: Clone the repository (recommended for developers):**
     ```
     git clone https://github.com/roeeov/AIprojectGD.git
     cd AIprojectGD
     code .
     ```
   - **Option B: Download and unzip:**
     - Go to https://github.com/roeeov/AIprojectGD
     - Click the "Code" button and select "Download ZIP"
     - Unzip the downloaded file to a folder
     - Open the unzipped folder in your text editor (VScode)

2. **Download the service account file:**
   - Go to this Google Drive folder: https://drive.google.com/drive/folders/1Xg9Y8D2GPADFKb52VUvifrdAdIGMZY8n?usp=drive_link
   - Download the file named `service_account.json`
   - Place the `service_account.json` file in the root directory of the project (same level as `engine.py`)

3. **Install required libraries:**
   ```
   pip install pygame torch numpy wandb pydrive2 google-auth google-api-python-client google-auth-oauthlib google-auth-httplib2
   ```

   Note: If you encounter issues with torch installation, visit https://pytorch.org/ for installation instructions specific to your system.

4. **Run the game:**
   ```
   python engine.py
   ```

### Additional Notes
- The game uses Google Drive for map management, which requires the service account file.
- For AI training features, wandb is used for logging.
- Ensure all data folders (data/, scripts/) are present as they contain game assets.