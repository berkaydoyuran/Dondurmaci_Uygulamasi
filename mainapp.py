import mysql.connector

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'sifreniz'
)

mycursor = mydb.cursor()
mycursor.execute('CREATE DATABASE IF NOT EXISTS dondurmaci')


class Dondurma:
    def __init__(self, tur, fiyat): 
        self.tur = tur
        self.fiyat = fiyat
        

class Calisan:
    def __init__(self,calisan_id,calisan_prim,):
        self.calisan_id = calisan_id
        self.calisan_prim = calisan_prim

class Musteri:
    def __init__(self,musteri_id,musteri_borc):
        self.musteri_id = musteri_id
        self.musteri_borc = musteri_borc


class MarasDondurmacisi():
    def __init__(self):
        self.baglanti_olustur()
        self.stok = {}
        self.satislar = [] 
        self.kar_zarar = 0
        self.tur_satislar = {} 
        self.primler = {}
        self.borclar = {}
        self.kayit = []

    def baglanti_olustur(self):
        self.baglanti = mysql.connector.connect(    
            host = 'localhost',
            user = 'root',
            password = 'sifreniz',
            database = 'dondurmaci'
            )
        self.cursor = self.baglanti.cursor()

        drop = "DROP TABLE Durum"
        self.cursor.execute(drop)
        stok_sorgu = "CREATE TABLE IF NOT EXISTS  Stok(tur VARCHAR(50), adet  INT)"
        self.cursor.execute(stok_sorgu)
        dondurma = "CREATE TABLE IF NOT EXISTS  Dondurma(tur VARCHAR(50), fiyat  INT)"
        self.cursor.execute(dondurma)
        satis = "CREATE TABLE IF NOT EXISTS  Satis(tur VARCHAR(50), adet INT, tercih VARCHAR(5) ,odeme_yontemi VARCHAR(50) ,musteri INT NULL )"
        self.cursor.execute(satis)
        durum = "CREATE TABLE IF NOT EXISTS  Durum( kar_zarar  INT DEFAULT 0 , bilgi VARCHAR(50) DEFAULT 'genel')"
        self.cursor.execute(durum)
        # calisan_sorgu = "CREATE TABLE IF NOT EXISTS  Calisanlar(id INT NOT NULL AUTO_INCREMENT, satis INT)"
        # self.cursor.execute(calisan_sorgu)

        self.baglanti.commit()

    def dondurmayi_tabloya_ekle(self,dondurma):
        if dondurma.tur not in self.kayit:
            sorgu = "INSERT INTO Dondurma(tur,fiyat) VALUES(%s,%s)"
            self.cursor.execute(sorgu,(dondurma.tur,dondurma.fiyat))
            self.kayit = list(self.kayit)
            self.kayit.append((dondurma.tur))
            self.baglanti.commit()
        else:
            print('DONDURMA ZATEN VAR DAYIIIII')

        
    def delete_stok(self):
        sorgu = "DELETE FROM Stok WHERE tur = 'cilek' "
        self.cursor.execute(sorgu)
        self.baglanti.commit()

    def stok_ekle(self,dondurma,adet):
        if dondurma.tur not in self.stok:
            print(dondurma.fiyat)
            self.stok[dondurma.tur] = adet 
            sorgu = "INSERT INTO Stok(tur,adet) VALUES(%s,%s)"
            self.cursor.execute(sorgu,(dondurma.tur,self.stok[dondurma.tur] ))
        else:
            self.stok[dondurma.tur] += adet
            print(self.stok[dondurma.tur])
            sorgu = "UPDATE Stok SET adet = %s WHERE tur = %s "
            self.cursor.execute(sorgu,(self.stok[dondurma.tur],dondurma.tur ))

        
        print(dondurma.tur)

        self.baglanti.commit()
    
    
    def satis_yap(self, dondurma, adet, tercih, odeme_yontemi, musteri = None):
        if dondurma.tur not in self.stok or self.stok[dondurma.tur] < adet:
            return "Stok yetersiz"
        self.stok[dondurma.tur] -= adet
        toplam_fiyat = adet * dondurma.fiyat
        
        if tercih == "kap":
            toplam_fiyat = toplam_fiyat * 1.5
        elif tercih == "kulah":
            toplam_fiyat = toplam_fiyat * 1

        if adet >= 9: # optional
            toplam_fiyat = (adet - adet//9) * dondurma.fiyat
            self.stok[dondurma.tur] -= adet//9
            self.kar_zarar -= (adet//9) * 3
        
        if odeme_yontemi == "veresiye":
            if not musteri:
                return "Musteri bilgileri eksik"
            else:
                self.satislar.append((dondurma.tur, adet, tercih, odeme_yontemi, musteri))
        else:
            self.satislar.append((dondurma.tur, adet, tercih, odeme_yontemi))
        self.kar_zarar += toplam_fiyat

        satis = "INSERT INTO Satis(tur,adet,tercih,odeme_yontemi,musteri) Values(%s,%s,%s,%s,%s)"
        self.cursor.execute(satis,(dondurma.tur,adet,tercih,odeme_yontemi,musteri))
        
        
        # durum = "INSERT INTO Durum(kar_zarar,bilgi) Values(%s)"
        # self.cursor.execute(durum,(self.kar_zarar))
        
        # durum = "UPDATE Durum SET kar_zarar = %s WHERE bilgi = %s "
        # self.cursor.execute(durum,(self.kar_zarar,'genel'))
        
        if dondurma.tur not in self.tur_satislar:
            self.tur_satislar[dondurma.tur] = adet
        else:
            self.tur_satislar[dondurma.tur] += adet

        print(sum(self.tur_satislar.values()))
        self.baglanti.commit()


    # def toplam_satis(self):
    #     return sum(self.tur_satislar.values())
    
    # def kar_zarar_durumu(self):
    #     return self.kar_zarar
    
    # def tur_satislar_getir(self):
    #     return self.tur_satislar
    
    # def drop_ice_cream(self, dondurma):
    #     if dondurma.tur in self.stok:
    #         self.stok[dondurma.tur] -= 1
    #         self.kar_zarar -= 3
    #         return f"{dondurma.tur} dusuruldu 1 top ucretsiz dondurma verildi"
    #     else:
    #         "Dondurma kalmadi"
