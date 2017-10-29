import face_recognition
import cv2
import time
import requests
import _thread

headers = {'Authorization': 'bearer 09667bf2d58afe60e6e54be0163a4cfc19e3f85ee814f269e84553ee1bb7a365'}
url = 'https://my.tanda.co/api/v2/clockins'

def clock_in(person):
    r = requests.post(url, headers=headers, data={
      "user_id": person['user_id'],
      "type": "clockout",
      "time": int(time.time() - 60)
    })

    if r.status_code < 300 and r.status_code >= 200:
        print("Success")
        person['clocked_in'] = True
    else:
        if r.status_code < 600 and r.status_code >= 400:
            print("Error")

# This is a super simple (but slow) example of running face recognition on live video from your webcam.
# There's a second example that's a little more complicated but runs faster.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
lachlan_image = face_recognition.load_image_file("Known_Faces/lachlan.jpeg")
lachlan_face_encoding = face_recognition.face_encodings(lachlan_image)[0]
brenton_image = face_recognition.load_image_file("Known_Faces/brenton.jpeg")
brenton_face_encoding = face_recognition.face_encodings(brenton_image)[0]

known_faces = [
    {
        'user_id': 450293,
        'name': "Lachlan",
        'face': lachlan_face_encoding,
        'clocked_in': False,
        'is_threading': False
    },{
        'user_id': 450311,
        'name': "Brenton",
        'face': brenton_face_encoding,
        'clocked_in': False,
        'is_threading': False
    }
]


while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        match = face_recognition.compare_faces([person['face'] for person in known_faces], face_encoding)
        name = "Unknown"
        index = 0

        for person in known_faces:
            if match[index]:
                name = person['name']
                if not person['clocked_in']:
                    if not person['is_threading']:
                        person['is_threading'] = True
                        _thread.start_new_thread(clock_in, (person,))
            index += 1

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
