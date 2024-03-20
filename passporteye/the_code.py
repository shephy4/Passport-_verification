class Passport_Atm_card:
    def __init__(self, passport, atm_card):
        import pytesseract
        #pytesseract.pytesseract.tesseract_cmd = r"full path to the exe file"
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.passport = passport
        self.atm_card = atm_card
    def extract_passport(self, passport):
        from passporteye import read_mrz
        self.passport = passport
        self.mrz = read_mrz(self.passport, save_roi=True)
        self.mrz_data = self.mrz.to_dict()
        #print(self.mrz_data)
        self.name = self.mrz_data['names'] + ' ' + self.mrz_data['surname']
        nin = self.mrz_data['personal_number'].split('<')[0]
        nationality = self.mrz_data['nationality']
        sex = self.mrz_data['sex']
        self.data = {'full_name' : self.name, 'nin': nin, 'sex': sex}
        print(self.data)
        return self.data

    def ocr_core(self, atm_card):
        self.atm_card = atm_card
        try:
            from PIL import Image
        except ImportError:
            import Image
        import pytesseract
        import re
        img = Image.open(self.atm_card)
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
        #print(self.text)
        return self.text
#jaccard similarities
    def compare_data(self,):
        mrz_data = self.extract_passport(self.passport)
        data = self.ocr_core(self.atm_card)
        intersection_cardinality = len(set.intersection(*[set(mrz_data), set(data)]))
        union_cardinality = len(set.union(*[set(mrz_data), set(data)]))
        result = intersection_cardinality / float(union_cardinality)
        if result >= 0.90:
            return (result, 'MATCH')
        else:
            return (result, 'NO MATCH')

passport = (r"C:\Users\T490\Downloads\passp.jpg")
atm_card = (r"C:\Users\T490\Downloads\scan0002_Original (1).jpg")
d = Passport_Atm_card(passport, atm_card)
result = d.compare_data()
print(result)
