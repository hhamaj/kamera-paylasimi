# kamera-paylasimi

Yerel ağdaki bilgisayarların kameralarını tek bir web sitesinden izlemek için basit bir sistem.

- **client/**: Kameralı cihazda çalışır. OpenCV ile kamerayı okur, açılışta kamera adını sorar ve görüntüyü WebSocket ile server'a gönderir. Bağlantı koparsa kendiliğinden yeniden bağlanır.
- **server/**: Flask + flask-sock. Client'lardan gelen kareleri alır, web sitesini servis eder ve kareleri tarayıcılara iletir.
- **web/**: Vue 3 + Vite ile yazılmış site. Bağlı kameraların hepsi grid halinde görünür. Birine tıklayınca büyür; büyük görünümde ‹ › butonları, alttaki küçük resimler veya ← → tuşlarıyla kameralar arasında geçilir, Esc ile kapanır.

Şifre yok; aynı yerel ağdaki herkes bağlanıp izleyebilir.

## Nasıl çalıştırılır

### Server (izleyen bilgisayar)

```bash
cd web && npm install && npm run build && cd ..
pip install -r server/requirements.txt
python run.py server
```

Tarayıcıda aç: `http://<server-ip>:5000`

### Client (kameralı bilgisayar)

```bash
pip install -r client/requirements.txt
python run.py client --server <server-ip>:5000
```

Açılınca kamera adını sorar; yazıp Enter'a basın, görüntü sitede çıkar.

İsteğe bağlı: `--camera 1` (başka kamera), `--fps 25`, `--quality 85`, `--width 1280 --height 720`.
Tüm seçenekler: `python run.py client -h`

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
