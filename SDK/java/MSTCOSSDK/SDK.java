/* package MSTCOSSDK; */
import java.net.*;
import java.io.*;
import java.util.Scanner;

public class SDK{
    String name;
    String color;

    Socket clientSocket;
    Scanner in;
    OutputStreamWriter out;

    public static final int Port = 55001;
    public SDK(String name_, String color_){
        name = name_;
        color = color_;
    }
    private void connect() throws InterruptedException{
        while(true){
            try{
                System.out.println("Connecteding with server");
                clientSocket = new Socket("localhost", Port);
                System.out.println("Connected with server");
                break;
            }catch(UnknownHostException e){
                //server not ready yet
            }catch(IOException e){
                //server not ready yet
            }
            Thread.sleep(100);
        }
        // get stream accessor
        while(true){
            try{
                out = new OutputStreamWriter(clientSocket.getOutputStream());
                out.flush();

                in = new Scanner(clientSocket.getInputStream());
                        /* new BufferedReader( */
                        /*     new InputStreamReader(clientSocket.getInputStream()))); */
                break;
            }catch(IOException ioException){
                /* System.out.println("get stream failed, retry"); */
                /* ioException.printStackTrace(); */
            }
        }
    }

    private static SDK _sdk = null;
    public static void StartGame(String[] info){
        if(_sdk != null) return;
        _sdk = new SDK(info[0], info[1]);
        try{
            _sdk.connect();

            OSInterface game = new OSInterface(_sdk.in, _sdk.out);
            game.Info(_sdk.name, _sdk.color);
            if(game.Running()){
                game.Data();
                AI myAI = new AI(game);
                while(game.Running()){
                    myAI.Iteration();
                    Thread.sleep(20);
                }
            }
        }catch(InterruptedException e){
            e.printStackTrace();
        }
    }
}

