/* package MSTCOSSDK; */
import java.util.List;
import java.util.ArrayList;
import java.io.*;

public class OSInterface{
    public static float MaxArmor = 1000;
    public static float Acceleration = 10;
    public static float MaxSpeed = 25;
    public static float AngularRate = 45;
    public static float ShipBoundingRadius = 15;
    public static float IslandBoundingRadius = 32;
    public static float CannonSpan = 4;
    public static float CannonAngle = 90;
    public static float CannonRange = 350;
    public static float[] ResourceRestoreRate = {0, 5, 10, 15, 25, 50};
    public static float ResourceRadius = 196;
    public static int MapWidth = 2048;
    public static int MapHeight = 2048;
    public static float RangeOfView = 400;

    //public fields
    public int Faction;
    public int TimeLeft;
    public List<ShipInfo> Ship;
    public List<ResourceInfo> Resource;

    //private fields
    private boolean _running;
    StreamTokenizer in;
    OutputStreamWriter out;

    // methods 
    public OSInterface(StreamTokenizer in_, OutputStreamWriter out_){
        _running = true;
        in = in_;
        out = out_;
        Resource = new ArrayList<ResourceInfo>();
        Ship = new ArrayList<ShipInfo>();
    }

    void Info(String name, String color){
        String[] args = {name, color};
        sendInstruction("Info", args);
    }
    public void Data(){
        String[] args = new String[0];
        if(sendInstruction("Data", args)){
            try{
                update();
                System.out.println("updated");
            }catch(IOException ioException){
                ioException.printStackTrace();
                System.out.println("error, data can not be updated!");
            }
        }
    }
    public void MoveTo(int shipId, float x, float y){
        String[] args = {Integer.toString(shipId), Float.toString(x), Float.toString(y)};
        sendInstruction("MoveTo", args);
    }
    public void Attack(int id1, int id2){
        String[] args = {Integer.toString(id1), Integer.toString(id2)};
        sendInstruction("Attack", args );
    }
    public void StartMoving(int shipId){
        String[] args = {Integer.toString(shipId)};
        sendInstruction("StartMoving", args );
    }
    public void StartRotating(int shipId, float angle){
        String[] args = {Float.toString(shipId)};
        sendInstruction("StartRotating", args );
    }
    public void StartRotatingTo(int shipId, float x, float y){
        String[] args = {Integer.toString(shipId), Float.toString(x), Float.toString(y)};
        sendInstruction("StartRotatingTo", args );
    }
    public void Stop(int shipId){
        String[] args = {Integer.toString(shipId)};
        sendInstruction("Stop", args );
    }
    public void StopMoving(int shipId){
        String[] args = {Integer.toString(shipId)};
        sendInstruction("StopMoving", args );
    }
    public void StopRotating(int shipId){
        String[] args = {Integer.toString(shipId)};
        sendInstruction("StopRotating", args );
    }


    public boolean Running(){
        return _running;
    }
    public void print(String s){
        System.out.println(s);
    }
    public void update() throws IOException{
        String attr, value;
        in.nextToken();
        in.nextToken();
        int n = (int)in.nval;
        for(int i = 0; i < n; i++){
            in.nextToken();
            attr = in.sval;
            /* //print */
            /* if(in.ttype == in.TT_WORD) */
            /*     print(attr); */
            /* else if(in.ttype == in.TT_NUMBER) */
            /*     print(""+in.nval); */

            in.nextToken();
            /* //print */
            /* if(in.ttype == in.TT_WORD) */
            /*     print(attr); */
            /* else if(in.ttype == in.TT_NUMBER) */
            /*     print(""+in.nval); */

            if(attr.equals("Faction")){
                Faction = (int)in.nval;
            }else if(attr.equals("Running")){
                _running = Boolean.parseBoolean(in.sval);
            }else if(attr.equals("Resource")){
                int n1 = (int)in.nval;
                Resource.clear();
                for(int j = 0; j < n1; j++){
                    ResourceInfo r = new ResourceInfo();
                    r.update(in);
                    Resource.add(r);
                }
            }else if(attr.equals("Ship")){
                int n1 = (int)in.nval;
                print("n2="+n1);
                Resource.clear();
                for(int j = 0; j < n1; j++){
                    ShipInfo ship = new ShipInfo();
                    ship.update(in);
                    Ship.add(ship);
                }
            }else{
                print("Unknown attribute: "+attr);
            }
        }
        print("<<<-------------");
    }
    public boolean sendInstruction(String cmd, String[] args){
        StringBuilder sbuilder = new StringBuilder();
        // add the time argument(unused now)
        sbuilder.append(cmd);
        sbuilder.append(" 0");
        for(String s : args) sbuilder.append(" ").append(s);
        sbuilder.append("\n");
        String inst = sbuilder.toString();
        try{
            out.write(inst);
            out.flush();
            System.out.println("sent: "+inst);
        }catch(IOException ioException){
            ioException.printStackTrace();
            System.out.println("error, send instruction failed!");
            _running = false;
            return false;
        }
        return true;
    }
}

