Simple python3 program to scrap event info from TECNA organizations

**How to set up**

**1. Download the Project ZIP**

  • Extract the ZIP file to a convenient location
    
  • Folder should contain tecna-scraper (Tutorial.txt, README.md, requirements.txt, topics.json, orgs.json, tecna_event_scraper.py)
  
 **2. Open Terminal or Command Prompt**
 
 • Navigate into the extracted folder: 
     
```cd ~/[Location of extracted zip]/tecna-scraper```
  
  **3. Set Up Environment (optional but good practice to do)**
      
```python3 -m venv venv```
   
 • for macOS/Linux
 
  ```source venv/bin/activate```
     
 • for Windows
 
  ```venv\Scripts\activate```
     
  
  **4. Install Required Packages**
  
   • when installing the following command:
     
  ```pip install -r requirements.txt```
   
   • you may get a notice about a new version of pip, please do so by following the notice prompt
  
  **5. Run the Script**
  
```python tecna_event_scraper.py```

   • When finished, the script will output output.csv — a table of events, organization names, and URLs.
