import pytesseract, pandas as pd, numpy as np, re, difflib
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from deepdiff import DeepDiff



class Identity_Verification:
    def __init__(self, passport, nin_slip):
        #pytesseract.pytesseract.tesseract_cmd = r"full path to the exe file"
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.passport = passport
        self.nin_slip = nin_slip
        
        
    def extract_passport(self, passport):
        from passporteye import read_mrz
        self.passport = passport
        self.mrz = read_mrz(self.passport, save_roi=True)
        
        if self.mrz is None:
            return {"error": "No MRZ data detected. Ensure the passport image is clear and properly aligned."}

        
        self.mrz_data = self.mrz.to_dict()
        if not self.mrz_data:
            return {"error": "Failed to extract MRZ data"}

        # Convert MRZ data into a DataFrame and save it
        self.df = pd.DataFrame([self.mrz_data])
        self.df.to_csv('bio_data.csv', index=False)
    
        # Safely extract necessary fields
        full_name = f"{self.mrz_data.get('names', 'Unknown')} {self.mrz_data.get('surname', 'Unknown')}"
        nin = self.mrz_data.get('personal_number', 'Unknown').split('<')[0]
        sex = self.mrz_data.get('sex', 'Unknown')
    
        return {"full_name": full_name, "nin": nin, "sex": sex}
            
    
    

    def ocr_core(self, nin_slip_image):
        self.nin_slip = nin_slip_image
        
        img = Image.open(self.nin_slip)
        img = img.convert("L")
        
        self.text = pytesseract.image_to_string(img)
        # Extract Surname
        surname_match = re.search(r"Surname:\s*([A-Za-z]+)", self.text)
        surname = surname_match.group(1) if surname_match else "Not Found"
        
        # Extract NIN
        nin_match = re.search(r"NIN:\s*(\d+)", self.text)
        nin = nin_match.group(1) if nin_match else "Not Found"
        
        # Extract First Name (Handling cases where '|' is present)
        fname_match = re.search(r"First Name:\s*\|?\s*([A-Za-z]+)", self.text)
        fname = fname_match.group(1) if fname_match else "Not Found"
        
        
        mname_match = re.search(r"Middle Name:\s*\|?\s*([A-Za-z]+)", self.text)
        mname = mname_match.group(1) if mname_match else "Not Found"
        
        
        # Ensure we start processing after "Gender:"
        gender_match = re.search(r"Gender:", self.text)
        if gender_match:
            text_after_gender = self.text[gender_match.end():]  # Get everything after "Gender:"
        else:
            text_after_gender = self.text  # If "Gender:" is not found, process entire text

        # Split the text into lines
        lines = text_after_gender.split("\n")
        
        # Initialize gender with a default value
        gender = "Not Found"

        # Extract last letter from each line
        for line in lines[-4:]:
            if "] " in line:
                gender = line.split(" ")[-1]

        name = fname+ ' '+ mname+ ' '+ surname
        self.text = {'full_name': name, 'nin': nin, 'sex': gender}
        #print(self.text)
        return self.text
    
    
    
#difflib,jaccard similarities
    def compare_data(self,):
        mrz_data = self.extract_passport(self.passport)
        nin_data = self.ocr_core(self.nin_slip)
        
        
        # Handle missing text scenarios
        if "error" in mrz_data:
            return ("NO MATCH", {"error": "Passport text extraction failed"})
        
        if "error" in nin_data:
            return ("NO MATCH", {"error": "NIN slip text extraction failed"})
            
        # Calculate Cosine Similarity
        # Convert dictionary values to a list of strings
        text1 = ' '.join(map(str, mrz_data.values()))
        text2 = ' '.join(map(str, nin_data.values()))
        # Convert the strings to vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        #cosine
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        print(f"Cosine Similarity: {similarity:.2f}")
        
        
        
        # Using the python inbuilt function difflib
        similarity = difflib.SequenceMatcher(None, str(mrz_data), str(nin_data)).ratio()
        print(f"Difflib Similarity Score: {similarity:.2f}")
        
        
        
        # Using the popular jaccard similarity formular, intersection /  union
        intersection_cardinality = len(set.intersection(*[set(mrz_data), set(nin_data)]))
        union_cardinality = len(set.union(*[set(mrz_data), set(nin_data)]))
        result = intersection_cardinality / float(union_cardinality)
    
        if result >= 0.90:

            return (f"MATCH : {result}", '')
        else:
            # Compute the differences in the dictionaries
            diff = DeepDiff(mrz_data, nin_data)
            return (f"NO MATCH : {result}", diff)
        

passport_ = (r"directory to International_Passport1.jpg")
ninslip = (r"directory to NIN.jpg")
d = Identity_Verification(passport_, ninslip)
result = d.compare_data()
print(result)
