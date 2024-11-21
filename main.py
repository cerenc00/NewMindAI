import pandas as pd
import matplotlib.pyplot as plt

# Veri setlerini yükleme
satis_verisi = pd.read_csv("C:\\Users\\Dell\\Downloads\\satis_verisi_5000.csv")
musteri_verisi = pd.read_csv("C:\\Users\\Dell\\Downloads\\musteri_verisi_5000_utf8.csv")

# Tarih sütununu datetime formatına çevir
satis_verisi['tarih'] = pd.to_datetime(satis_verisi['tarih'])

# Veri setlerinin ilk 5 satırını görüntüleme
print(satis_verisi.head())
print(musteri_verisi.head())

# Eksik verileri kontrol etme
print("Satış Verisindeki Eksik Değerler:")
print(satis_verisi.isnull().sum())
print("\nMüşteri Verisindeki Eksik Değerler:")
print(musteri_verisi.isnull().sum())

# Fiyat sütununu float tipine dönüştür ve eksik değerleri doldur
satis_verisi['fiyat'] = pd.to_numeric(satis_verisi['fiyat'], errors='coerce')
satis_verisi['fiyat'] = satis_verisi['fiyat'].fillna(satis_verisi['fiyat'].median())

# Aykırı değerleri tespit etme ve düzeltme fonksiyonu
def aykiri_degerleri_tespit_ve_duzelt(df, sutun_adi):
    Q1 = df[sutun_adi].quantile(0.25)
    Q3 = df[sutun_adi].quantile(0.75)
    IQR = Q3 - Q1
    alt_sinir = Q1 - 1.5 * IQR
    ust_sinir = Q3 + 1.5 * IQR
    print(f"{sutun_adi} - Alt Sınır: {alt_sinir}, Üst Sınır: {ust_sinir}")
    df[sutun_adi] = df[sutun_adi].clip(lower=alt_sinir, upper=ust_sinir)
    return df

# Fiyat ve harcama miktarı sütunları için aykırı değer düzeltme
satis_verisi = aykiri_degerleri_tespit_ve_duzelt(satis_verisi, 'fiyat')
musteri_verisi = aykiri_degerleri_tespit_ve_duzelt(musteri_verisi, 'harcama_miktari')

# Birleştirilmiş veri seti
genel_veri = pd.merge(satis_verisi, musteri_verisi, on='musteri_id', how='inner')
print(genel_veri.head())
print(genel_veri.describe())


# Haftalık ve aylık satış hesaplamaları
satis_verisi.set_index('tarih', inplace=True)
haftalik_satis = satis_verisi.resample('W').agg({'toplam_satis': 'sum'})
aylik_satis = satis_verisi.resample('ME').agg({'toplam_satis': 'sum'})

# Satış trendlerini görselleştirme
plt.figure(figsize=(16, 12))  # Grafik boyutunu artırdık

# Haftalık toplam satış grafiği
plt.subplot(2, 1, 1)
plt.plot(haftalik_satis.index, haftalik_satis['toplam_satis'], marker='o', color='blue', label='Haftalık Satış')
plt.title('Haftalık Toplam Satış Trendleri')
plt.xlabel('Tarih')
plt.ylabel('Toplam Satış')
plt.grid(True)

# Aylık toplam satış grafiği
plt.subplot(2, 1, 2)
plt.plot(aylik_satis.index, aylik_satis['toplam_satis'], marker='o', color='green', label='Aylık Satış')
plt.title('Aylık Toplam Satış Trendleri')
plt.xlabel('Tarih')
plt.ylabel('Toplam Satış')
plt.grid(True)

# Grafik düzenini manuel olarak ayarlamak
plt.subplots_adjust(hspace=0.5, top=0.95, bottom=0.05, left=0.1, right=0.9)
plt.show()

# tarih sütununu kontrol et ve geri döndür
if 'tarih' not in satis_verisi.columns:
    satis_verisi.reset_index(inplace=True)

# tarih sütununu datetime formatına çeviriyoruz
satis_verisi['tarih'] = pd.to_datetime(satis_verisi['tarih'])

# tarih sütununu indeks olarak ayarlıyoruz
satis_verisi.set_index('tarih', inplace=True)

# Her ayın ilk ve son satış günlerini buluyoruz
ilk_gunler = satis_verisi.resample('MS').apply(lambda x: x.index.min()).reset_index()
ilk_gunler = ilk_gunler.rename(columns={ilk_gunler.columns[0]: 'tarih', ilk_gunler.columns[1]: 'ilk_gun'})  # İlk sütun adı düzeltildi

son_gunler = satis_verisi.resample('ME').apply(lambda x: x.index.max()).reset_index()
son_gunler = son_gunler.rename(columns={son_gunler.columns[0]: 'tarih', son_gunler.columns[1]: 'son_gun'})  # Son sütun adı düzeltildi

# İlk ve son günlerde NaT değerlerini kaldırma
print("\nİlk Günler:")
print(ilk_gunler.columns)  # Sütun isimlerini kontrol edin
print(ilk_gunler.head())

print("\nSon Günler:")
print(son_gunler.columns)  # Sütun isimlerini kontrol edin
print(son_gunler.head())

# NaT değerlerini kaldırma
ilk_gunler.dropna(subset=['ilk_gun'], inplace=True)
son_gunler.dropna(subset=['son_gun'], inplace=True)

# Sadece gerekli sütunları bırakma
ilk_gunler = ilk_gunler[['tarih', 'ilk_gun']]
son_gunler = son_gunler[['tarih', 'son_gun']]

# Merge işlemini yapıyoruz
ilk_son_gunler = pd.merge(ilk_gunler, son_gunler, on="tarih", how="outer")

# Haftalık ürün satışlarını hesaplıyoruz
haftalik_urun_satis = satis_verisi.resample('W').agg({'adet': 'sum'}).reset_index()

print("\nHaftalık Ürün Satışları:")
print(haftalik_urun_satis.head())

# Grafik oluşturma
plt.figure(figsize=(10, 6))
plt.plot(haftalik_urun_satis['tarih'], haftalik_urun_satis['adet'], marker='o', linestyle='-', color='b', label='Haftalık Satış')
plt.title("Haftalık Ürün Satışları")
plt.xlabel("Tarih")
plt.ylabel("Satılan Adet")
plt.grid()
plt.legend()
plt.tight_layout()
plt.subplots_adjust(hspace=0.5, top=0.9)
plt.show()


### GÖREV 3: Ürün Kategorileri Bazında Satış Analizi

# Kategorilere göre toplam satış miktarını hesaplama
satis_verisi['toplam_satis'] = pd.to_numeric(satis_verisi['toplam_satis'], errors='coerce')  # 'toplam_satis' sütununu sayıya çeviriyoruz
kategori_satilari = satis_verisi.groupby('kategori').agg({'toplam_satis': 'sum'}).reset_index()

# Her kategorinin toplam satışlar içindeki oranını hesaplama
kategori_satilari['oran'] = kategori_satilari['toplam_satis'] / kategori_satilari['toplam_satis'].sum() * 100

print("\nÜrün Kategorilerine Göre Toplam Satışlar ve Yüzde Oranları:")
print(kategori_satilari)

## Görev3.2
# Yaş gruplarını oluşturma
bins = [0, 25, 35, 50, 100]  # Yaş aralıkları (18-25, 26-35, 36-50, 50+)
labels = ['18-25', '26-35', '36-50', '50+']
musteri_verisi['yas_grubu'] = pd.cut(musteri_verisi['yas'], bins=bins, labels=labels, right=False)

# Yaş gruplarına göre toplam satışları hesaplama
musteri_satis = pd.merge(satis_verisi, musteri_verisi, on='musteri_id', how='inner')
yas_grubu_satis = musteri_satis.groupby('yas_grubu', observed=False).agg({'toplam_satis': 'sum'}).reset_index()

# Yaş gruplarına göre satış oranını hesaplama
yas_grubu_satis['oran'] = yas_grubu_satis['toplam_satis'] / yas_grubu_satis['toplam_satis'].sum() * 100

print("\nYaş Gruplarına Göre Toplam Satışlar ve Yüzde Oranları:")
print(yas_grubu_satis)
print(musteri_verisi.columns)
##Görev3.3
# Kadın ve erkeklerin harcama miktarlarının ortalamalarını hesaplayalım
cinsiyet_harcama = musteri_verisi.groupby('cinsiyet')['harcama_miktari'].mean().reset_index()

# Kadınlar ve erkeklerin ortalama harcama miktarlarını yazdıralım
print("\nKadın ve Erkeklerin Ortalama Harcama Miktarları:")
print(cinsiyet_harcama)
# Kadın ve erkeklerin harcama miktarları arasındaki fark
kadın_harcama = musteri_verisi[musteri_verisi['cinsiyet'] == 'Kadın']['harcama_miktari'].mean()
erkek_harcama = musteri_verisi[musteri_verisi['cinsiyet'] == 'Erkek']['harcama_miktari'].mean()

# Farkı yazdıralım
print(f"\nKadınların Ortalama Harcama Miktarı: {kadın_harcama}")
print(f"Erkeklerin Ortalama Harcama Miktarı: {erkek_harcama}")
print(f"Fark: {kadın_harcama - erkek_harcama}")


# Şehir bazında toplam harcama miktarını hesaplayalım
sehir_harcama = musteri_verisi.groupby('sehir')['harcama_miktari'].sum().reset_index()

# Şehirleri toplam harcama miktarına göre azalan sırayla sıralayalım
sehir_harcama_sorted = sehir_harcama.sort_values(by='harcama_miktari', ascending=False).reset_index(drop=True)

# Şehirlerin harcama miktarlarını yazdıralım
print("\nŞehirler Bazında Toplam Harcama Miktarı (En Yüksekten Düşüğe):")
print(sehir_harcama_sorted)
