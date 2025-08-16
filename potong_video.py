import os
import argparse  # Import library untuk parsing argumen
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip

def potong_video_youtube(url, waktu_mulai, waktu_selesai, nama_output):
    """
    Fungsi untuk mengunduh video YouTube dengan resolusi terbaik,
    memotongnya sesuai waktu yang ditentukan, dan menyimpannya.
    """
    temp_video_file = "temp_video.mp4"
    temp_audio_file = "temp_audio.mp4"
    
    try:
        print(f"Mencari video dari URL: {url}")
        yt = YouTube(url)
        print(f"Video ditemukan: '{yt.title}'")

        # --- Bagian Download ---
        print("\n1. Mengunduh video (resolusi terbaik)...")
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        if not video_stream:
            print("Stream adaptive tidak ditemukan, mencoba stream progressive...")
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        video_stream.download(filename=temp_video_file)
        print(f"   -> Video berhasil diunduh (Resolusi: {video_stream.resolution})")

        print("2. Mengunduh audio (kualitas terbaik)...")
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
        audio_stream.download(filename=temp_audio_file)
        print(f"   -> Audio berhasil diunduh (Bitrate: {audio_stream.abr})")

        # --- Bagian Pemotongan dan Penggabungan ---
        print(f"\n3. Memotong video dari {waktu_mulai} sampai {waktu_selesai}...")
        
        with VideoFileClip(temp_video_file) as video_clip, AudioFileClip(temp_audio_file) as audio_clip:
            video_potongan = video_clip.subclip(waktu_mulai, waktu_selesai)
            audio_potongan = audio_clip.subclip(waktu_mulai, waktu_selesai)
            
            video_final = video_potongan.set_audio(audio_potongan)
            
            print(f"4. Menyimpan hasil ke file '{nama_output}'...")
            video_final.write_videofile(
                nama_output,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
        
        print(f"\n✅  Selesai! Video berhasil dipotong dan disimpan sebagai '{nama_output}'")

    except Exception as e:
        print(f"\n❌ Terjadi kesalahan: {e}")
        exit(1) # Keluar dengan status error

    finally:
        # --- Bagian Pembersihan ---
        print("\nMembersihkan file sementara...")
        if os.path.exists(temp_video_file):
            os.remove(temp_video_file)
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

# --- Bagian Utama untuk Menjalankan Skrip ---
if __name__ == "__main__":
    # Setup parser untuk menerima argumen dari command line
    parser = argparse.ArgumentParser(description="Potong video YouTube melalui URL.")
    parser.add_argument("--url", required=True, help="URL video YouTube yang akan dipotong.")
    parser.add_argument("--start", required=True, help="Waktu mulai pemotongan (format MM:SS atau HH:MM:SS).")
    parser.add_argument("--end", required=True, help="Waktu selesai pemotongan (format MM:SS atau HH:MM:SS).")
    parser.add_argument("--output", required=True, help="Nama file output (contoh: hasil.mp4).")
    
    args = parser.parse_args()
    
    # Menjalankan fungsi utama dengan argumen yang diberikan
    potong_video_youtube(args.url, args.start, args.end, args.output)
          
