import network
import time
from machine import Pin
import dht
import ujson
import urequests

# Konfigurasi WiFi
SSID = "Wokwi-GUEST"
PASSWORD = ""

# Konfigurasi Cloud (menggunakan HTTP POST untuk simplicity)
CLOUD_ENDPOINT = "https://api.thingspeak.com/update.json"
THINGSPEAK_API_KEY = "YOUR_API_KEY_HERE"  # Ganti dengan API key Anda

# Atau gunakan webhook.site untuk testing cepat
WEBHOOK_URL = "https://webhook.site/unique-url"  # Ganti dengan URL Anda

# Setup Hardware
led = Pin(2, Pin.OUT)
sensor = dht.DHT22(Pin(15))

# Status LED
led_status = False

def connect_wifi():
    """Koneksi ke WiFi"""
    print("Menghubungkan ke WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print("\nWiFi Terhubung!")
        print("IP Address:", wlan.ifconfig()[0])
        return True
    else:
        print("\nGagal terhubung ke WiFi")
        return False

def read_sensor():
    """Membaca data dari sensor DHT22"""
    try:
        sensor.measure()
        temp = sensor.temperature()
        humid = sensor.humidity()
        return temp, humid
    except Exception as e:
        print(f"Error membaca sensor: {e}")
        return None, None

def send_to_cloud(temp, humid):
    """Kirim data ke cloud menggunakan HTTP POST"""
    try:
        data = {
            "temperature": temp,
            "humidity": humid,
            "led_status": "ON" if led_status else "OFF",
            "timestamp": time.time()
        }
        
        # Uncomment salah satu metode dibawah:
        
        # Metode 1: ThingSpeak
        # url = f"{CLOUD_ENDPOINT}?api_key={THINGSPEAK_API_KEY}&field1={temp}&field2={humid}"
        # response = urequests.get(url)
        
        # Metode 2: Webhook (untuk testing)
        response = urequests.post(WEBHOOK_URL, json=data)
        
        print(f"✅ Data terkirim: {response.status_code}")
        response.close()
        return True
        
    except Exception as e:
        print(f"❌ Error mengirim data: {e}")
        return False

def check_led_command():
    """Simulasi pengecekan perintah dari cloud"""
    # Dalam implementasi nyata, ini akan mengecek dari cloud
    # Untuk demo, LED bisa dikontrol manual dari kode
    pass

def toggle_led():
    """Toggle LED untuk demo"""
    global led_status
    led_status = not led_status
    if led_status:
        led.on()
        print("💡 LED: ON")
    else:
        led.off()
        print("💡 LED: OFF")

def main():
    """Program utama"""
    print("\n" + "="*50)
    print("🚀 ESP32 IoT System - Starting...")
    print("="*50 + "\n")
    
    # Koneksi WiFi
    if not connect_wifi():
        print("⚠️ Program dihentikan - WiFi tidak terhubung")
        return
    
    print("\n" + "="*50)
    print("✅ Sistem IoT Berjalan")
    print("="*50)
    print("📊 Monitoring: Suhu & Kelembaban")
    print("💡 Control: LED (Pin 2)")
    print("⏱️  Interval: 5 detik")
    print("="*50 + "\n")
    
    counter = 0
    led_toggle_interval = 4  # Toggle LED setiap 20 detik (4 x 5 detik)
    
    try:
        while True:
            # Baca sensor
            temp, humid = read_sensor()
            
            if temp is not None and humid is not None:
                print(f"\n📡 Pengiriman Data #{counter + 1}")
                print(f"🌡️  Suhu       : {temp}°C")
                print(f"💧 Kelembaban : {humid}%")
                print(f"💡 LED Status : {'ON' if led_status else 'OFF'}")
                
                # Kirim ke cloud
                send_to_cloud(temp, humid)
                
                counter += 1
                
                # Toggle LED setiap beberapa kali (untuk demo)
                if counter % led_toggle_interval == 0:
                    toggle_led()
                
                print("-" * 50)
            
            time.sleep(5)  # Kirim data setiap 5 detik
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Program dihentikan oleh user")
        led.off()
        print("👋 Bye!")

# Jalankan program
if __name__ == "__main__":
    main()