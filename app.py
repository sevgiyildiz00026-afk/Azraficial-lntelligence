import json
import os
import streamlit as st
from groq import Groq

# Dosya yolları (Kullanıcıları ve sohbetleri kaydetmek için)
USERS_FILE = "users.json"
CHAT_FILE = "chats.json"


# Veri okuma ve yazma fonksiyonları
def load_data(file_path):
  if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except:
        return {}
  return {}


def save_data(file_path, data):
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Sayfa Ayarları
st.set_page_config(
    page_title="Azraficial Intelligence", page_icon="📖", layout="centered"
)

# --- TASARIM VE RENK AYARLARI (CSS) ---
st.markdown("""
   <style>
   /* Kullanıcı mesaj balonu (Turkuaz) - Kullanici avatari olanlar */
   [data-testid="stChatMessage"]:has(img[alt="user"]),
   [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
       background-color: #50dede !important;
       border-radius: 15px;
       padding: 10px;
   }
   
   /* Karakter / Asistan mesaj balonu (Açık Sarı) - Bot avatari olanlar */
   [data-testid="stChatMessage"]:has(img[alt="assistant"]),
   [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAsisstant"]) {
       background-color: #f2f1aa !important;
       border-radius: 15px;
       padding: 10px;
   }
   </style>
""",
    unsafe_allow_html=True,
)

# Oturum durumları (Session State) başlatma
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state.logged_in:
  st.title("📖 Yeni Bir Hikayeye Başlamak İçin Giriş Yapınız")
  st.write(
      "Devam etmek için bir kullanıcı adı ve şifre belirle"
  )

  tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

  users = load_data(USERS_FILE)

  with tab1:
    login_user = st.text_input("Kullanıcı Adı", key="login_u")
    login_pass = st.text_input("Şifre", type="password", key="login_p")
    if st.button("Giriş Yap"):
      if (
          login_user in users
          and users[login_user] == login_pass  # Basit şifre kontrolü
      ):
        st.session_state.logged_in = True
        st.session_state.username = login_user
        st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
        st.rerun()
      else:
        st.error("Kullanıcı adı veya şifre hatalı!")

  with tab2:
    reg_user = st.text_input("Yeni Kullanıcı Adı", key="reg_u")
    reg_pass = st.text_input("Yeni Şifre", type="password", key="reg_p")
    if st.button("Kayıt Ol ve Giriş Yap"):
      if reg_user in users:
        st.warning("Bu kullanıcı adı zaten alınmış.")
      elif reg_user.strip() == "":
        st.warning("Kullanıcı adı boş olamaz.")
      else:
        users[reg_user] = reg_pass
        save_data(USERS_FILE, users)
        st.session_state.logged_in = True
        st.session_state.username = reg_user
        st.success("Kayıt oluşturuldu! Yönlendiriliyorsunuz...")
        st.rerun()

# --- ANA SOHBET EKRANI ---
else:
  st.sidebar.title(f"Hoş geldin, {st.session_state.username}! 🌟")

  # Groq API Anahtarı İsteme
  api_key = st.sidebar.text_input("Groq API Anahtarın", type="password")

  st.sidebar.markdown("---")
  st.sidebar.subheader("🎭 Karakter Seçimi")
  secilen_karakter = st.sidebar.selectbox(
      "Kimle konuşmak istiyorsun?",
      ["Karan (Konuşkan ve biraz zorba, Zengin popüler)", "Ege (Neşeli ve Esprili, Karan'ın bestiesi)", "Suna (Neşeli, kafa dengi, z kuşağı, en yakın arkadaş)", "AzIn (Bilgili yapay zeka botun)"],
  )

  if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

  st.title(f"💬 Sohbet Odası: {secilen_karakter.split(' ')[0]}")

  if not api_key:
    st.warning("Lütfen sol menüden Groq API anahtarını gir.")
  else:
    client = Groq(api_key=api_key)

    # Sohbet geçmişini kullanıcıya ve karaktere göre saklama
    chats = load_data(CHAT_FILE)
    room_key = f"{st.session_state.username}_{secilen_karakter.split(' ')[0]}"

    if room_key not in chats:
      chats[room_key] = []

    # Geçmiş mesajları ekranda göster
    for message in chats[room_key]:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Kullanıcıdan mesaj al
    if prompt := st.chat_input("Karaktere bir şey yaz..."):
      chats[room_key].append({"role": "user", "content": prompt})
      with st.chat_message("user"):
        st.markdown(prompt)

      # Karakterin kişilik sistem talimatı (System Prompt)
      if "Karan" in secilen_karakter:
          system_prompt = (
              "Sen lise 11. sınıfa giden Karan adlı konuşkan, okuldaki herkesi tanıyan ve herkesin tanıdığı, herkese laf atan, herkesin lafını dinlemesine alışmış, tüm kızlara laf atsa da hiç biriyle başrol kız karakter kadar samimi olmayan ve yakışıklı bir erkek karakter sin. Sen sadece seçilen karakterin rolünü oynayan bir arkadaşsın. Doğal ve sade replikler yaz. Senaryo gereği birden fazla karakter canlandırman gerekirse, karakterlerin adını belirterek (Örn: [Karan]: ..., [Ege]: ...) replikler sun. Kullanıcı hangi dilde yazarsa (Türkçe, İngilizce veya Hollandaca) o dilde doğal bir şekilde yanıt ver. Gerektiğinde akıcı bir şekilde Hollandaca (Nederlands) veya İngilizce (English) konuşabilirsin."
         )

      elif "AzIn" in secilen_karakter:
          system_prompt = (
              "Sen yardimsever, bilgili ve anlayisli bir yapay zeka asistanisin. Kullanicinin sordugu sorulara dogru, net, mantikli ve aciklayici yanitlar verirsin. Karmasik konulari basit bir dille anlatirsin. Kullanici hangi dilde yazarsa (Turkce, Ingilizce veya Hollandaca) o dilde yanit verirsin."
         )

      else:
        system_prompt = (
            "Sen Suna adında günlük hayatta, sıkılınca yada konuşmak istediğimde sana yazdığım, z kuşağı bir kadın karaktersin. Sen sadece samimi, emojiler kullanarak, random atarak ve gerçek bir arkadaşımmışsın gibi replikler yaz. Kullanıcı hangi dilde yazarsa (Türkçe, İngilizce veya Hollandaca) o dilde doğal bir şekilde yanıt ver. Gerektiğinde akıcı bir şekilde Hollandaca (Nederlands) veya İngilizce (English) konuşabilirsin."
         )

      # Groq AI'dan yanıt al
      messages_for_ai = [{"role": "system", "content": system_prompt}] + chats[
          room_key
      ]

      try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b", 
            messages=messages_for_ai,
            temperature=0.7,   # Anlamsız sağmalamaları engeller, daha mantıklı cevaplar üretir
            max_tokens=500,     # Dakikalık limit hatasını (429) engeller
        )
        ai_response = response.choices[0].message.content

        with st.chat_message("assistant"):
          st.markdown(ai_response)

        chats[room_key].append({"role": "assistant", "content": ai_response})
        save_data(CHAT_FILE, chats)

      except Exception as e:
        st.error(f"Bir hata oluştu: {e}")