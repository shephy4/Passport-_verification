import pytesseract, pandas as pd, numpy as np

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
        self.mrz_data = self.mrz.to_dict()
        data_ = []
        data = dict(self.mrz_data)
        data_.append(data)
        print(data_)
        self.df = pd.DataFrame(data_)
        self.df.to_csv('bio_data.csv')
        print(self.df)
        self.name = self.mrz_data['names'] + ' ' + self.mrz_data['surname']
        nin = self.mrz_data['personal_number'].split('<')[0]
        nationality = self.mrz_data['nationality']
        sex = self.mrz_data['sex']
        self.data = {'full_name' : self.name, 'nin': nin, 'sex': sex}
        print(self.data)
        return self.data

    def ocr_core(self, nin_slip_image):
        self.nin_slip = nin_slip_image
        try:
            from PIL import Image
        except ImportError:
            import Image
        import pytesseract
        import re
        img = Image.open(self.nin_slip)
        img = img.convert("L")
        
        self.text = pytesseract.image_to_string(img)
        self.text = self.text.split(':')[3:][:-1]
        surname = self.text[0].strip().replace('\n\n', ' ').split(' ')[1]
        nin = self.text[1].strip().split()[0]
        fname = self.text[2].replace('\n\n', ' ').split()[0]
        mname = self.text[4].replace('\n\n', ' ').split()[0]
        sex = self.text[5].replace('\n\n', ' ').split()[0]
        name = fname+ ' '+ mname+ ' '+ surname
        self.text = {'full_name': name, 'nin': nin, 'sex': sex}
        print(self.text)
        #self.text = re.sub('[^A-Z\s]+', '', str(self.text))
        #self.text = re.sub('\s+', ' ', str(self.text))
        return self.text
#jaccard similarities
    def compare_data(self,):
        mrz_data = self.extract_passport(self.passport)
        data = self.ocr_core(self.nin_slip)
        intersection_cardinality = len(set.intersection(*[set(mrz_data), set(data)]))
        union_cardinality = len(set.union(*[set(mrz_data), set(data)]))
        result = intersection_cardinality / float(union_cardinality)
        if result >= 0.90:

            return (f"MATCH : {result}", self.df)
        else:
            return (f"NO MATCH : {result}", "")

passport_ = (r"C:\Users\T490\Downloads\passp.jpg")
ninslip = (r"C:\Users\T490\Downloads\scan0002_Original (1).jpg")
d = Identity_Verification(passport_, ninslip)
result = d.compare_data()
print(result)
