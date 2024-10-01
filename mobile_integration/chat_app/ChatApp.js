import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, TextInput, Button, ScrollView } from 'react-native';
import WebSocket from 'ws';

const ChatApp = () => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [ws, setWs] = useState(null);

    useEffect(() => {
        const socket = new WebSocket('ws://YOUR_PC_IP_ADDRESS:8765');
        setWs(socket);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setChatHistory(prevHistory => [...prevHistory, { sender: 'Snowball', text: data.response }]);
        };

        return () => socket.close();
    }, []);

    const sendMessage = () => {
        if (ws && message.trim()) {
            const userMessage = { message: message.trim() };
            ws.send(JSON.stringify(userMessage));
            setChatHistory(prevHistory => [...prevHistory, { sender: 'You', text: message }]);
            setMessage('');
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#000', padding: 10 }}>
            <ScrollView style={{ flex: 1, marginBottom: 10 }}>
                {chatHistory.map((msg, index) => (
                    <View key={index} style={{ marginVertical: 5 }}>
                        <Text style={{ color: msg.sender === 'You' ? '#fff' : '#4caf50' }}>
                            {msg.sender}: {msg.text}
                        </Text>
                    </View>
                ))}
            </ScrollView>
            <View style={{ flexDirection: 'row', marginBottom: 10 }}>
                <TextInput
                    style={{ flex: 1, backgroundColor: '#fff', padding: 10, borderRadius: 5 }}
                    placeholder="Type your message"
                    value={message}
                    onChangeText={setMessage}
                />
                <Button title="Send" onPress={sendMessage} />
            </View>
        </SafeAreaView>
    );
};

export default ChatApp;
