package com.example.snowballmod;

import org.py4j.GatewayServer;

public class SnowballPythonConnector {
    private SnowballHandler snowballHandler;

    public SnowballPythonConnector() {
        // Setup Py4J gateway
        GatewayServer gatewayServer = new GatewayServer();
        gatewayServer.start();
        this.snowballHandler = (SnowballHandler) gatewayServer.getPythonServerEntryPoint(new Class[] { SnowballHandler.class });
    }

    public String sendMessageToSnowball(String message) {
        return this.snowballHandler.processInput(message);
    }
}
