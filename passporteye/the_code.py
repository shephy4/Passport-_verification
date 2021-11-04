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
        self.mrz_data = self.mrz_data['names'] + ' ' + self.mrz_data['surname']
        return self.mrz_data

    def ocr_core(self, atm_card):
        self.atm_card = atm_card
        try:
            from PIL import Image
        except ImportError:
            import Image
        import pytesseract
        import re
        self.text = pytesseract.image_to_string(Image.open(self.atm_card))
        self.text = re.sub('[^A-Z\s]+', '', str(self.text))
        self.text = re.sub('\s+', ' ', str(self.text))
        return self.text
#jaccard similarities
    def compare_data(self,):
        mrz_data = self.extract_passport(self.passport)
        data = self.ocr_core(self.atm_card)
        intersection_cardinality = len(set.intersection(*[set(mrz_data), set(data)]))
        union_cardinality = len(set.union(*[set(mrz_data), set(data)]))
        result = intersection_cardinality / float(union_cardinality)
        if result >= 90:
            return (result, 'MATCH')
        else:
            return (result, 'NO MATCH')

passport = (r'C:\Users\DELL\Downloads\international_pass_1.png')
atm_card = (r'C:\Users\DELL\Downloads\atm_card.png')
d = Passport_Atm_card(passport, atm_card)
result = d.compare_data()
print(result)
