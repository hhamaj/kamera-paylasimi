# kamera-paylasimi

Yerel ağdaki bilgisayarların kameralarını tek bir web sitesinden izlemek için basit bir sistem.

- **client/**: Kameralı cihazda çalışır. OpenCV ile kamerayı okur, açılışta kamera adını sorar ve görüntüyü WebSocket ile server'a gönderir. Bağlantı koparsa kendiliğinden yeniden bağlanır.
- **server/**: Flask + flask-sock. Client'lardan gelen kareleri alır, web sitesini servis eder ve kareleri tarayıcılara iletir.
- **web/**: Vue 3 + Vite ile yazılmış site. Bağlı kameraların hepsi grid halinde görünür. Birine tıklayınca büyür; büyük görünümde ‹ › butonları, alttaki küçük resimler veya ← → tuşlarıyla kameralar arasında geçilir, Esc ile kapanır.

Şifre yok; aynı yerel ağdaki herkes bağlanıp izleyebilir.

## Kurulum

Her şey kök dizindeki `run.py` ile çalıştırılır; ilk argüman modu seçer:

```bash
python run.py server [seçenekler]
python run.py client [seçenekler]
python run.py client -h          # modun seçeneklerini gösterir
```

### Server (izleme yapılacak bilgisayar)

```bash
# 1) Web sitesini build et (Node.js gerekir, bir kez yapılması yeter)
cd web
npm install
npm run build        # çıktı server/static/ klasörüne yazılır

# 2) Server'ı çalıştır
cd ..
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r server/requirements.txt
python run.py server             # varsayılan: 0.0.0.0:5000 (--host, --port ile değişir)
```

Site: `http://<server-ip>:5000`

### Client (kameralı cihaz)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r client/requirements.txt
python run.py client --server 192.168.1.10:5000
```

Açılınca `Kamera adi:` sorulur; girilen isim sitede görünür.

Seçenekler:

| Parametre   | Varsayılan       | Açıklama                                   |
|-------------|------------------|--------------------------------------------|
| `--server`  | `localhost:5000` | Server adresi                              |
| `--camera`  | `0`              | Kamera numarası (ikinci kamera için `1`)   |
| `--width`   | `640`            | Genişlik                                   |
| `--height`  | `480`            | Yükseklik                                  |
| `--fps`     | `15`             | Saniyedeki kare sayısı                     |
| `--quality` | `70`             | JPEG kalitesi (1-100)                      |

Bir cihazdaki iki kamerayı paylaşmak için client'ı iki kez, farklı `--camera` değerleriyle açın.

## Geliştirme

Site üzerinde çalışırken server'ı açık bırakıp ayrıca:

```bash
cd web
npm run dev
```

Vite dev server `/ws` isteklerini `localhost:5000`'deki Flask'a yönlendirir.

## Nasıl çalışır

- Client `/ws/camera`'ya bağlanır, önce `{"name": "..."}` JSON'u, sonra JPEG karelerini binary mesaj olarak gönderir.
- Tarayıcı `/ws/view`'a tek bir WebSocket ile bağlanır. Server kamera listesi değiştikçe JSON, her yeni karede `4 byte kamera id + JPEG` binary mesajı gönderir.
- Server her kameranın sadece son karesini tutar; yavaş bir izleyici eski kareleri biriktirmez, en günceli alır.
- Tüm kameralar tek WebSocket'ten geldiği için tarayıcının aynı adrese açabileceği bağlantı sınırına (~6) takılmaz.
