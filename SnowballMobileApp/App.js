import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, Button, ScrollView, TouchableOpacity, Alert } from 'react-native';
import WebSocket from 'react-native-websocket';
import Voice from 'react-native-voice';

export default function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [voiceInput, setVoiceInput] = useState('');
  const wsUrl = 'ws://YOUR_PC_IP:5000'; // WebSocket server on Snowball PC
  let ws;

  useEffect(() => {
    // Initialize WebSocket connection
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to Snowball WebSocket server.');
    };

    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      setMessages([...messages, { sender: 'Snowball', text: response.reply }]);
    };

    ws.onerror = (error) => {
      console.log(`WebSocket Error: ${error.message}`);
      Alert.alert('Error', 'WebSocket connection error.');
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    return () => {
      ws.close();  // Clean up WebSocket connection when component is unmounted
    };
  }, [messages]);

  // Handle text input submission
  const sendCommand = () => {
    if (input.trim()) {
      setMessages([...messages, { sender: 'User', text: input }]);
      ws.send(JSON.stringify({ command: input }));
      setInput('');
    }
  };

  // Voice command handling
  const startVoiceRecognition = () => {
    Voice.start('en-US');
  };

  useEffect(() => {
    Voice.onSpeechResults = (result) => {
      const voiceMessage = result.value[0];
      setVoiceInput(voiceMessage);
      setMessages([...messages, { sender: 'User', text: voiceMessage }]);
      ws.send(JSON.stringify({ command: voiceMessage }));
    };

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, [messages]);

  return (
    <View style={styles.container}>
      <ScrollView style={styles.chatContainer}>
        {messages.map((msg, idx) => (
          <Text key={idx} style={msg.sender === 'User' ? styles.userMsg : styles.aiMsg}>{msg.text}</Text>
        ))}
      </ScrollView>
      <TextInput
        style={styles.input}
        value={input}
        onChangeText={setInput}
        placeholder="Type a command..."
      />
      <View style={styles.buttonContainer}>
        <Button title="Send" onPress={sendCommand} />
        <TouchableOpacity style={styles.voiceButton} onPress={startVoiceRecognition}>
          <Text>🎙️ Speak</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', justifyContent: 'center', padding: 20 },
  chatContainer: { flex: 1, marginBottom: 10 },
  userMsg: { textAlign: 'right', backgroundColor: '#DCF8C6', marginBottom: 5, padding: 10, borderRadius: 5 },
  aiMsg: { textAlign: 'left', backgroundColor: '#F1F0F0', marginBottom: 5, padding: 10, borderRadius: 5 },
  input: { height: 40, borderColor: 'gray', borderWidth: 1, marginBottom: 10, paddingHorizontal: 10 },
  buttonContainer: { flexDirection: 'row', justifyContent: 'space-between' },
  voiceButton: { backgroundColor: '#0A74DA', padding: 10, borderRadius: 5 },
});
