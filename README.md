
# **Voice Assistant ReadMe**

## **Objective**

This project aims to develop a **voice assistant** using **LiveKit's Voice Pipeline Agent**. It includes a mechanism to validate and trim long audio responses before **Text-to-Speech (TTS)** processing. If the estimated audio length exceeds 60 seconds, the system will return a trimmed version of the audio centered around its middle segment.

## **Features**

- **LiveKit Voice Pipeline Integration**: Setup and utilize **LiveKit's Voice Pipeline Agent**.
- **Audio Length Validation**: Estimate the length of TTS-generated audio before processing.
- **Flask Backend for Validation**: A dedicated server to validate and trim long audio responses.
- **Seamless Communication**: Establish connectivity between **LiveKit** and the backend.
- **User Interface**: Provide a UI for interaction and testing.

## **Project Setup**

### 1. **Clone and Set Up LiveKit Voice Pipeline Agent**

```bash
git clone https://github.com/vishal-jangid-dotsquares/voice-assistant.git
cd voice-assistant
```

### 2. **Install Dependencies**

Ensure you have **Node.js** (v20.18.3 or newer) and **npm** installed. Also, install **Python** and **pip**.

### 3. **Create Accounts and Generate API Keys**

Register on the following platforms and generate the required API keys mentioned in **.env.example**:

- **LiveKit**: [LiveKit Cloud](https://www.livekit.io)
- **Rime**: [Rime AI](https://www.rime.com)
- **Groq**: [Groq](https://www.groq.com)
- **Speechmatics**: [Speechmatics](https://www.speechmatics.com)

### 4. **Setup Execution Permissions**

Provide execution permissions to the setup and start scripts:

```bash
chmod +x setup.sh start.sh
```

### 5. **Run Setup Script**

Execute the setup script to configure the project:

```bash
./setup.sh
```

### 6. **Start the Servers**

Run the start script to launch the services:

```bash
./start.sh
```

### 7. **Access the Voice Assistant**

Open the Next.js local URL: [http://localhost:3000/](http://localhost:3000/)

Alternatively, access via the ngrok URL (no local setup required): [https://c485-136-232-169-245.ngrok-free.app](https://c485-136-232-169-245.ngrok-free.app)

## **Notes**

- Ensure that all API keys are correctly configured in the **.env** file.
- If facing issues, verify dependencies and restart the servers.
- The system will automatically trim any audio exceeding 60 seconds before processing through TTS.