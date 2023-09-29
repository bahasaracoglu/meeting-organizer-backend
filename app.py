import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)

# SQLite veritabanına bağlanma
conn = sqlite3.connect('meetings.db', check_same_thread=False)
cursor = conn.cursor()

# Veritabanında toplantılar tablosunu oluşturma
cursor.execute('''CREATE TABLE IF NOT EXISTS meetings
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   topic TEXT,
                   date TEXT,
                   start_time TEXT,
                   end_time TEXT,
                   participants TEXT)''')
conn.commit()

# Seed fonksiyonu


def seed_meetings():
    # Verilerin varlığını kontrol et
    cursor.execute("SELECT COUNT(*) FROM meetings")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_meetings = [
            {"topic": "Toplantı 1", "date": "2023-09-30", "start_time": "09:00",
                "end_time": "10:00", "participants": "John, Alice"},
            {"topic": "Toplantı 2", "date": "2023-10-01", "start_time": "14:00",
                "end_time": "15:30", "participants": "Bob, Carol"}
        ]

        for meeting in sample_meetings:
            cursor.execute("INSERT INTO meetings (topic, date, start_time, end_time, participants) VALUES (?, ?, ?, ?, ?)",
                           (meeting['topic'], meeting['date'], meeting['start_time'], meeting['end_time'], meeting['participants']))

        conn.commit()


# Flask uygulamanızın başlangıcında seed fonksiyonunu çağırın
if __name__ == "__main__":
    with app.app_context():
        seed_meetings()

# Ana sayfa için HTML şablonunu görüntüle


# Tüm toplantıları al


@app.route('/meetings', methods=['GET'])
def get_meetings():
    cursor.execute("SELECT * FROM meetings")
    meetings = cursor.fetchall()

    # Toplantıları JSON formatında döndürün
    meeting_list = []
    for meeting in meetings:
        meeting_dict = {
            "id": meeting[0],
            "topic": meeting[1],
            "date": meeting[2],
            "start_time": meeting[3],
            "end_time": meeting[4],
            "participants": meeting[5]
        }
        meeting_list.append(meeting_dict)

    return jsonify(meeting_list)


@app.route('/meetings', methods=['POST'])
def create_meeting():
    data = request.get_json()
    if not data or not all(data.values()):
        # 400 Bad Request
        return jsonify({"error": "Boş veya eksik veri gönderilemez"}), 400
    print(data)

    # Yeni toplantıyı veritabanına ekleyin
    cursor.execute("INSERT INTO meetings (topic, date, start_time, end_time, participants) VALUES (?, ?, ?, ?, ?)",
                   (data['topic'], data['date'], data['start_time'], data['end_time'], data['participants']))
    conn.commit()

    return jsonify({"message": "Yeni toplantı oluşturuldu"}), 201


@app.route('/meetings/<int:id>', methods=['PUT'])
def update_meeting(id):
    # Yeni verileri alın
    data = request.get_json()
    if not data or not all(data.values()):
        # 400 Bad Request
        return jsonify({"error": "Boş veya eksik veri gönderilemez"}), 400

    # Veritabanında belirli bir toplantıyı güncelle
    cursor.execute("UPDATE meetings SET topic=?, date=?, start_time=?, end_time=?, participants=? WHERE id=?",
                   (data['topic'], data['date'], data['start_time'], data['end_time'], data['participants'], id))
    conn.commit()

    return jsonify({"message": "Toplantı güncellendi"}), 200


@app.route('/meetings/<int:id>', methods=['DELETE'])
def delete_meeting(id):
    print(id)
    # Veritabanında belirli bir toplantıyı sil
    cursor.execute("DELETE FROM meetings WHERE id=?", (id,))
    conn.commit()

    return jsonify({"message": "Toplantı silindi"}), 200


if __name__ == '__main__':
    app.run(debug=True)
