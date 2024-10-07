package com.example.snowballmod;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.network.chat.Component;
import net.minecraft.server.commands.CommandSourceStack;
import com.mojang.brigadier.Command;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import org.py4j.GatewayServer;

@Mod("snowballmod")
public class SnowballMod {
    public SnowballMod() {
        // Register event bus
        Mod.EventBusSubscriber.Bus.FORGE.register(this);
    }

    @SubscribeEvent
    public void onCommandRegister(RegisterCommandsEvent event) {
        event.getDispatcher().register(
            Commands.literal("snowball")
                .then(Commands.argument("input", StringArgumentType.greedyString())
                .executes(this::sendToSnowball))
        );
    }

    private int sendToSnowball(CommandContext<CommandSourceStack> context) {
        String input = StringArgumentType.getString(context, "input");
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        // Send input to Python via Py4J
        SnowballPythonConnector connector = new SnowballPythonConnector();
        String response = connector.sendMessageToSnowball(input);

        // Respond back in-game
        player.sendSystemMessage(Component.literal("Snowball Response: " + response));
        return Command.SINGLE_SUCCESS;
    }
}
